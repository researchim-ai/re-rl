# re_rl/tasks/group_theory_task.py

import random
from sympy import mod_inverse, gcd, randprime, totient, factorint
from sympy.combinatorics import Permutation
from sympy.combinatorics.permutations import Cycle
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any

class GroupTheoryTask(BaseMathTask):
    """
    Генератор задач по теории групп: обратные элементы, порядки элементов, свойства групп.
    Параметры:
    - task_type: "inverse_element", "element_order", "group_properties"
    - group_type: "cyclic", "symmetric"
    - modulus: модуль для циклических групп
    - degree: степень для симметрических групп
    """
    def __init__(self, task_type="inverse_element", group_type="cyclic", 
                 modulus=None, degree=3, element=None, property_type=None,
                 language: str = "ru", detail_level: int = 3):
        self.task_type = task_type.lower()
        self.group_type = group_type.lower()
        self.modulus = modulus
        self.degree = degree
        self.element = element
        self.property_type = property_type
        super().__init__("", language, detail_level)

    def generate_group(self):
        if self.group_type == "cyclic":
            if not self.modulus:
                self.modulus = randprime(5, 20) if self.task_type == "inverse_element" else random.randint(5, 15)
            
            if self.element is None:
                if self.task_type == "inverse_element":
                    self.element = random.randint(2, self.modulus-1)
                    while gcd(self.element, self.modulus) != 1:
                        self.element = random.randint(2, self.modulus-1)
                else:
                    self.element = random.randint(0, self.modulus-1)
        
        elif self.group_type == "symmetric":
            self.element = Permutation.random(self.degree)

    def _create_problem_description(self):
        self.generate_group()
        
        if self.group_type == "cyclic":
            group_desc_ru = (f"мультипликативной группе по модулю {self.modulus}" 
                            if self.task_type == "inverse_element" 
                            else f"аддитивной группе по модулю {self.modulus}")
            group_desc_en = (f"multiplicative group modulo {self.modulus}" 
                           if self.task_type == "inverse_element" 
                           else f"additive group modulo {self.modulus}")
        else:
            group_desc_ru = f"симметрической группе S_{self.degree}"
            group_desc_en = f"symmetric group S_{self.degree}"
        
        if self.task_type == "group_properties":
            if not self.property_type:
                self.property_type = random.choice(["is_abelian", "order"])

            templates = {
                "is_abelian": {
                    "ru": f"Является ли {group_desc_ru} абелевой группой? Обоснуйте свой ответ.",
                    "en": f"Is the group {group_desc_en} abelian? Justify your answer."
                },
                "order": {
                    "ru": f"Какой порядок у группы {group_desc_ru}?",
                    "en": f"What is the order of the group {group_desc_en}?"
                }
            }
            return templates[self.property_type][self.language]

        templates = {
            "inverse_element": {
                "ru": f"Найдите обратный элемент для элемента {self.element} в {group_desc_ru}.",
                "en": f"Find the inverse element for {self.element} in {group_desc_en}."
            },
            "element_order": {
                "ru": f"Определите порядок элемента {self.element} в {group_desc_ru}.",
                "en": f"Determine the order of element {self.element} in {group_desc_en}."
            }
        }
        return templates[self.task_type][self.language]

    def solve(self):
        self.description = self._create_problem_description()
        steps = []
        
        if self.task_type == "group_properties":
            if self.group_type == "cyclic":
                if self.property_type == "is_abelian":
                    is_abelian = True
                    reason = "Все циклические группы являются абелевыми."
                    self.final_answer = "Да"
                elif self.property_type == "order":
                    order = self.modulus
                    reason = f"Порядок аддитивной группы по модулю n равен n. Порядок мультипликативной группы взаимно простых элементов по модулю n равен функции Эйлера phi(n)."
                    self.final_answer = str(order)
            
            elif self.group_type == "symmetric":
                if self.property_type == "is_abelian":
                    is_abelian = self.degree <= 2
                    reason = f"Симметрическая группа S_n является абелевой только при n <= 2."
                    self.final_answer = "Да" if is_abelian else "Нет"
                elif self.property_type == "order":
                    order = 1
                    for i in range(1, self.degree + 1):
                        order *= i
                    reason = f"Порядок симметрической группы S_n равен n! = {order}."
                    self.final_answer = str(order)
            
            steps.append(f"Свойство: {self.property_type}")
            steps.append(f"Ответ: {self.final_answer}")
            steps.append(f"Обоснование: {reason}")

        elif self.group_type == "cyclic":
            if self.task_type == "inverse_element":
                inv = mod_inverse(self.element, self.modulus)
                steps.append(f"Шаг 1: Находим НОД({self.element}, {self.modulus}) = {gcd(self.element, self.modulus)}")
                steps.append(f"Шаг 2: Применяем расширенный алгоритм Евклида для нахождения обратного элемента: {inv}")
                self.final_answer = str(inv)
            
            elif self.task_type == "element_order":
                if "additive" in self.description:
                    # Для (Z_n,+): порядок равен n / gcd(a,n)
                    order = self.modulus // gcd(self.element, self.modulus)
                else:
                    # Мультипликативная группа (Z_n)^*
                    if gcd(self.element, self.modulus) != 1:
                        # элемент не принадлежит группе, порядок не определён
                        order = 0
                    else:
                        phi_n = totient(self.modulus)
                        order = phi_n
                        # сокращаем order, проверяя простые множители φ(n)
                        for p in factorint(phi_n).keys():
                            while order % p == 0 and pow(self.element, order // p, self.modulus) == 1:
                                order //= p
                steps.append(f"Порядок элемента вычислен через свойства циклической группы: {order}")
                self.final_answer = str(order)

        elif self.group_type == "symmetric":
            if self.task_type == "inverse_element":
                # Для перестановок обратный элемент - обратная перестановка
                inv_perm = self.element ** (-1)
                steps.append(f"Шаг 1: Находим обратную перестановку для {self.element}")
                steps.append(f"Шаг 2: Проверяем композицию: {self.element} ∘ {inv_perm} = {self.element * inv_perm}")
                self.final_answer = str(inv_perm)
                
            elif self.task_type == "element_order":
                # Порядок перестановки - НОК длин циклов
                order = self.element.order()
                cycle_decomp = self.element.cycle_structure
                steps.append(f"Шаг 1: Цикловая структура: {cycle_decomp}")
                steps.append(f"Шаг 2: Вычисляем НОК длин циклов: {order}")
                self.final_answer = str(order)

        self.solution_steps.extend(steps)

    @classmethod
    def generate_random_task(cls, task_type=None, group_type=None, 
                            language: str = "ru", detail_level: int = 3):
        task_type = task_type or random.choice(["inverse_element", "element_order", "group_properties"])
        group_type = group_type or random.choice(["cyclic", "symmetric"])
        
        if task_type == "group_properties":
             return cls(task_type=task_type, group_type=group_type, 
                 language=language, detail_level=detail_level, property_type=random.choice(["is_abelian", "order"]))

        return cls(task_type=task_type, group_type=group_type, 
                 language=language, detail_level=detail_level)