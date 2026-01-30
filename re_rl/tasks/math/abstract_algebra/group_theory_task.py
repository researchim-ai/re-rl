# re_rl/tasks/group_theory_task.py

"""
GroupTheoryTask — задачи по теории групп.

Поддерживаемые типы:
- inverse_element: обратные элементы
- element_order: порядок элемента
- group_properties: свойства группы (абелевость, порядок)
"""

import random
from sympy import mod_inverse, gcd, randprime, totient, factorint
from sympy.combinatorics import Permutation
from sympy.combinatorics.permutations import Cycle
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any


class GroupTheoryTask(BaseMathTask):
    """
    Генератор задач по теории групп.
    
    Параметры:
    - task_type: "inverse_element", "element_order", "group_properties"
    - group_type: "cyclic", "symmetric"
    - modulus: модуль для циклических групп
    - degree: степень для симметрических групп
    """
    
    TASK_TYPES = ["inverse_element", "element_order", "group_properties"]
    GROUP_TYPES = ["cyclic", "symmetric"]
    
    def __init__(
        self,
        task_type: str = "inverse_element",
        group_type: str = "cyclic",
        modulus: int = None,
        degree: int = 3,
        element=None,
        property_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        output_format: str = "text",
        reasoning_mode: bool = False
    ):
        self.task_type = task_type.lower()
        self.group_type = group_type.lower()
        self.modulus = modulus
        self.degree = degree
        self.element = element
        self.property_type = property_type
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Сначала генерируем данные задачи
        self._generate_group()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _generate_group(self):
        """Генерирует данные группы."""
        if self.group_type == "cyclic":
            if not self.modulus:
                self.modulus = randprime(5, 20) if self.task_type == "inverse_element" else random.randint(5, 15)
            
            if self.element is None:
                if self.task_type == "inverse_element":
                    self.element = random.randint(2, self.modulus - 1)
                    while gcd(self.element, self.modulus) != 1:
                        self.element = random.randint(2, self.modulus - 1)
                else:
                    self.element = random.randint(0, self.modulus - 1)
        
        elif self.group_type == "symmetric":
            self.element = Permutation.random(self.degree)

    def _get_group_desc(self) -> str:
        """Возвращает описание группы на нужном языке."""
        templates = PROMPT_TEMPLATES.get("group_theory", {}).get("group_names", {})
        
        if self.group_type == "cyclic":
            if self.task_type == "inverse_element":
                template = templates.get("multiplicative_cyclic", {}).get(self.language, "")
            else:
                template = templates.get("additive_cyclic", {}).get(self.language, "")
            return template.format(n=self.modulus)
        else:
            template = templates.get("symmetric", {}).get(self.language, "")
            return template.format(n=self.degree)

    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("group_theory", {}).get("problem", {})
        group_desc = self._get_group_desc()
        
        if self.task_type == "group_properties":
            if not self.property_type:
                self.property_type = random.choice(["is_abelian", "order"])
            
            if self.property_type == "is_abelian":
                template = templates.get("is_abelian", {}).get(self.language, "")
            else:
                template = templates.get("group_order", {}).get(self.language, "")
            return template.format(group_desc=group_desc)
        
        elif self.task_type == "inverse_element":
            template = templates.get("inverse_element", {}).get(self.language, "")
            return template.format(element=self.element, group_desc=group_desc)
        
        elif self.task_type == "element_order":
            template = templates.get("element_order", {}).get(self.language, "")
            return template.format(element=self.element, group_desc=group_desc)
        
        return ""

    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("group_theory", {}).get("steps", {})
        reasons_templates = PROMPT_TEMPLATES.get("group_theory", {}).get("reasons", {})
        
        if self.task_type == "group_properties":
            self._solve_group_properties(steps_templates, reasons_templates)
        elif self.group_type == "cyclic":
            self._solve_cyclic(steps_templates)
        elif self.group_type == "symmetric":
            self._solve_symmetric(steps_templates)
        

    def _solve_group_properties(self, templates, reasons):
        """Решает задачу на свойства группы."""
        if self.group_type == "cyclic":
            if self.property_type == "is_abelian":
                self.final_answer = "Да" if self.language == "ru" else "Yes"
                reason = reasons.get("cyclic_abelian", {}).get(self.language, "")
            else:  # order
                order = self.modulus
                self.final_answer = str(order)
                reason = reasons.get("additive_order", {}).get(self.language, "")
        
        elif self.group_type == "symmetric":
            if self.property_type == "is_abelian":
                is_abelian = self.degree <= 2
                self.final_answer = ("Да" if self.language == "ru" else "Yes") if is_abelian else ("Нет" if self.language == "ru" else "No")
                reason = reasons.get("symmetric_not_abelian", {}).get(self.language, "")
            else:  # order
                order = 1
                for i in range(1, self.degree + 1):
                    order *= i
                self.final_answer = str(order)
                reason_template = reasons.get("symmetric_order", {}).get(self.language, "")
                reason = reason_template.format(factorial=order)
        
        template = templates.get("property_check", {}).get(self.language, "")
        self.solution_steps.append(template.format(property=self.property_type))
        
        template2 = templates.get("answer_with_reason", {}).get(self.language, "")
        self.solution_steps.append(template2.format(answer=self.final_answer, reason=reason))

    def _solve_cyclic(self, templates):
        """Решает задачу для циклической группы."""
        if self.task_type == "inverse_element":
            inv = mod_inverse(self.element, self.modulus)
            
            template1 = templates.get("gcd_check", {}).get(self.language, "")
            self.solution_steps.append(template1.format(
                a=self.element, b=self.modulus, gcd=gcd(self.element, self.modulus)
            ))
            
            template2 = templates.get("extended_euclidean", {}).get(self.language, "")
            self.solution_steps.append(template2.format(inverse=inv))
            
            self.final_answer = str(inv)
        
        elif self.task_type == "element_order":
            # Для аддитивной группы: порядок = n / gcd(a, n)
            order = self.modulus // gcd(self.element, self.modulus)
            
            template = templates.get("order_computed", {}).get(self.language, "")
            self.solution_steps.append(template.format(order=order))
            
            self.final_answer = str(order)

    def _solve_symmetric(self, templates):
        """Решает задачу для симметрической группы."""
        if self.task_type == "inverse_element":
            inv_perm = self.element ** (-1)
            
            template1 = templates.get("inverse_permutation", {}).get(self.language, "")
            self.solution_steps.append(template1.format(element=self.element))
            
            template2 = templates.get("verify_composition", {}).get(self.language, "")
            self.solution_steps.append(template2.format(
                element=self.element, inverse=inv_perm, result=self.element * inv_perm
            ))
            
            self.final_answer = str(inv_perm)
        
        elif self.task_type == "element_order":
            order = self.element.order()
            cycle_decomp = self.element.cycle_structure
            
            template1 = templates.get("cycle_structure", {}).get(self.language, "")
            self.solution_steps.append(template1.format(structure=cycle_decomp))
            
            template2 = templates.get("lcm_cycles", {}).get(self.language, "")
            self.solution_steps.append(template2.format(order=order))
            
            self.final_answer = str(order)

    def get_task_type(self) -> str:
        return "group_theory"

    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        group_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        reasoning_mode: bool = False
    ):
        """Генерирует случайную задачу по теории групп."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        group_type = group_type or random.choice(cls.GROUP_TYPES)
        
        property_type = None
        if task_type == "group_properties":
            property_type = random.choice(["is_abelian", "order"])
        
        return cls(
            task_type=task_type,
            group_type=group_type,
            language=language,
            detail_level=detail_level,
            property_type=property_type,
            reasoning_mode=reasoning_mode
        )
