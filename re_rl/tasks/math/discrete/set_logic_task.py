# re_rl/tasks/set_logic_task.py

"""
SetLogicTask — задачи на множества и логику.

Поддерживаемые типы:
- union: объединение множеств
- intersection: пересечение множеств
- difference: разность множеств
- symmetric_difference: симметрическая разность
- complement: дополнение
- cardinality: мощность объединения
- power_set: мощность степени множества
- cartesian_product: декартово произведение
- boolean_simplify: упрощение логических выражений
- truth_table: таблица истинности
- venn_problem: задачи на диаграммы Венна
"""

import random
from typing import List, Dict, Any, Optional, Set, FrozenSet, ClassVar
from dataclasses import dataclass
from itertools import product as iter_product

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class SetLogicTask(BaseMathTask):
    """Задачи на множества и логику."""
    
    TASK_TYPES = [
        "union", "intersection", "difference", "symmetric_difference",
        "complement", "cardinality", "power_set", "cartesian_product",
        "boolean_simplify", "truth_table", "venn_problem"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_set_size": 5, "max_element": 10},
        2: {"max_set_size": 6, "max_element": 15},
        3: {"max_set_size": 7, "max_element": 20},
        4: {"max_set_size": 8, "max_element": 25},
        5: {"max_set_size": 9, "max_element": 30},
        6: {"max_set_size": 10, "max_element": 40},
        7: {"max_set_size": 12, "max_element": 50},
        8: {"max_set_size": 14, "max_element": 75},
        9: {"max_set_size": 16, "max_element": 100},
        10: {"max_set_size": 20, "max_element": 150},
    }
    
    def __init__(
        self,
        task_type: str = "union",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self.kwargs = kwargs
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_set_size = kwargs.get("max_set_size", preset.get("max_set_size", 9))
        self.max_element = kwargs.get("max_element", preset.get("max_element", 30))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_random_set(self, min_size: int = 2) -> Set[int]:
        """Генерирует случайное множество."""
        size = random.randint(min_size, self.max_set_size)
        return set(random.sample(range(1, self.max_element + 1), size))
    
    def _set_to_str(self, s: Set) -> str:
        """Преобразует множество в строку."""
        return "{" + ", ".join(map(str, sorted(s))) + "}"
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type in ["union", "intersection", "difference", "symmetric_difference", "cartesian_product"]:
            self.set_a = self._generate_random_set()
            self.set_b = self._generate_random_set()
            # Для интересных задач добавляем пересечение
            if self.task_type in ["intersection", "difference", "symmetric_difference"]:
                common = set(random.sample(list(self.set_a), min(2, len(self.set_a))))
                self.set_b = self.set_b.union(common)
        
        elif self.task_type == "complement":
            self.set_a = self._generate_random_set()
            # Универсальное множество включает A и ещё элементы
            extra = set(random.sample(
                [x for x in range(1, self.max_element + 1) if x not in self.set_a],
                min(5, self.max_element - len(self.set_a))
            ))
            self.universal = self.set_a.union(extra)
        
        elif self.task_type == "cardinality":
            self.card_a = random.randint(10, 50)
            self.card_b = random.randint(10, 50)
            self.card_intersection = random.randint(1, min(self.card_a, self.card_b) - 1)
        
        elif self.task_type == "power_set":
            self.n = random.randint(2, min(6, self.max_set_size))
        
        elif self.task_type == "boolean_simplify":
            self._generate_boolean_expression()
        
        elif self.task_type == "truth_table":
            self._generate_truth_table_expression()
        
        elif self.task_type == "venn_problem":
            self._generate_venn_problem()
    
    def _generate_boolean_expression(self):
        """Генерирует логическое выражение для упрощения."""
        expressions = [
            ("A ∧ (A ∨ B)", "A", "absorption"),
            ("A ∨ (A ∧ B)", "A", "absorption"),
            ("¬(A ∧ B)", "¬A ∨ ¬B", "de_morgan"),
            ("¬(A ∨ B)", "¬A ∧ ¬B", "de_morgan"),
            ("A ∧ ¬A", "⊥ (ложь)", "contradiction"),
            ("A ∨ ¬A", "⊤ (истина)", "tautology"),
            ("A ∧ A", "A", "idempotent"),
            ("A ∨ A", "A", "idempotent"),
            ("A ∧ ⊤", "A", "identity"),
            ("A ∨ ⊥", "A", "identity"),
        ]
        
        self.expression, self.simplified, self.law_name = random.choice(expressions)
    
    def _generate_truth_table_expression(self):
        """Генерирует выражение для таблицы истинности."""
        expressions = [
            "A ∧ B",
            "A ∨ B",
            "A → B",
            "A ↔ B",
            "¬A ∨ B",
            "(A ∧ B) ∨ C",
        ]
        
        self.expression = random.choice(expressions[:4])  # Простые выражения
        self.num_vars = 2 if "C" not in self.expression else 3
    
    def _generate_venn_problem(self):
        """Генерирует задачу на диаграмму Венна."""
        self.total = random.randint(50, 200)
        
        # Генерируем количества для двух множеств
        self.only_a = random.randint(10, self.total // 3)
        self.only_b = random.randint(10, self.total // 3)
        self.both = random.randint(5, min(self.only_a, self.only_b))
        self.neither = self.total - self.only_a - self.only_b - self.both
        
        if self.neither < 0:
            self.neither = 0
            self.total = self.only_a + self.only_b + self.both
        
        if self.language == "ru":
            self.desc = (f"{self.only_a + self.both} человек знают английский, "
                        f"{self.only_b + self.both} человек знают французский, "
                        f"{self.both} человек знают оба языка.")
            self.question = "не знают ни одного из этих языков"
        else:
            self.desc = (f"{self.only_a + self.both} people know English, "
                        f"{self.only_b + self.both} people know French, "
                        f"{self.both} people know both languages.")
            self.question = "know neither language"
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("set_logic", {}).get("problem", {})
        
        if self.task_type == "union":
            template = templates.get("union", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), set_b=self._set_to_str(self.set_b))
        
        elif self.task_type == "intersection":
            template = templates.get("intersection", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), set_b=self._set_to_str(self.set_b))
        
        elif self.task_type == "difference":
            template = templates.get("difference", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), set_b=self._set_to_str(self.set_b))
        
        elif self.task_type == "symmetric_difference":
            template = templates.get("symmetric_difference", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), set_b=self._set_to_str(self.set_b))
        
        elif self.task_type == "complement":
            template = templates.get("complement", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), universal=self._set_to_str(self.universal))
        
        elif self.task_type == "cardinality":
            template = templates.get("cardinality", {}).get(self.language, "")
            return template.format(
                card_a=self.card_a, card_b=self.card_b, card_intersection=self.card_intersection
            )
        
        elif self.task_type == "power_set":
            template = templates.get("power_set", {}).get(self.language, "")
            return template.format(n=self.n)
        
        elif self.task_type == "cartesian_product":
            template = templates.get("cartesian_product", {}).get(self.language, "")
            return template.format(set_a=self._set_to_str(self.set_a), set_b=self._set_to_str(self.set_b))
        
        elif self.task_type == "boolean_simplify":
            template = templates.get("boolean_simplify", {}).get(self.language, "")
            return template.format(expression=self.expression)
        
        elif self.task_type == "truth_table":
            template = templates.get("truth_table", {}).get(self.language, "")
            return template.format(expression=self.expression)
        
        elif self.task_type == "venn_problem":
            template = templates.get("venn_problem", {}).get(self.language, "")
            return template.format(total=self.total, desc=self.desc, question=self.question)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("set_logic", {}).get("steps", {})
        
        if self.task_type == "union":
            self._solve_union(steps_templates)
        elif self.task_type == "intersection":
            self._solve_intersection(steps_templates)
        elif self.task_type == "difference":
            self._solve_difference(steps_templates)
        elif self.task_type == "symmetric_difference":
            self._solve_symmetric_difference(steps_templates)
        elif self.task_type == "complement":
            self._solve_complement(steps_templates)
        elif self.task_type == "cardinality":
            self._solve_cardinality(steps_templates)
        elif self.task_type == "power_set":
            self._solve_power_set(steps_templates)
        elif self.task_type == "cartesian_product":
            self._solve_cartesian_product(steps_templates)
        elif self.task_type == "boolean_simplify":
            self._solve_boolean_simplify(steps_templates)
        elif self.task_type == "truth_table":
            self._solve_truth_table(steps_templates)
        elif self.task_type == "venn_problem":
            self._solve_venn_problem(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_union(self, templates):
        """Объединение множеств."""
        result = self.set_a.union(self.set_b)
        
        template = templates.get("union_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, set_a=self._set_to_str(self.set_a),
            set_b=self._set_to_str(self.set_b), result=self._set_to_str(result)
        ))
        
        self.final_answer = self._set_to_str(result)
    
    def _solve_intersection(self, templates):
        """Пересечение множеств."""
        result = self.set_a.intersection(self.set_b)
        
        template = templates.get("intersection_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, set_a=self._set_to_str(self.set_a),
            set_b=self._set_to_str(self.set_b), result=self._set_to_str(result)
        ))
        
        self.final_answer = self._set_to_str(result)
    
    def _solve_difference(self, templates):
        """Разность множеств."""
        result = self.set_a.difference(self.set_b)
        
        template = templates.get("difference_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=self._set_to_str(result)))
        
        self.final_answer = self._set_to_str(result)
    
    def _solve_symmetric_difference(self, templates):
        """Симметрическая разность."""
        result = self.set_a.symmetric_difference(self.set_b)
        
        template = templates.get("symmetric_diff_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=self._set_to_str(result)))
        
        self.final_answer = self._set_to_str(result)
    
    def _solve_complement(self, templates):
        """Дополнение множества."""
        result = self.universal.difference(self.set_a)
        
        template = templates.get("complement_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=self._set_to_str(result)))
        
        self.final_answer = self._set_to_str(result)
    
    def _solve_cardinality(self, templates):
        """Мощность объединения."""
        result = self.card_a + self.card_b - self.card_intersection
        
        template = templates.get("cardinality_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, card_a=self.card_a, card_b=self.card_b,
            card_intersection=self.card_intersection, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_power_set(self, templates):
        """Мощность степени множества."""
        result = 2 ** self.n
        
        template = templates.get("power_set_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, result=result))
        
        self.final_answer = str(result)
    
    def _solve_cartesian_product(self, templates):
        """Декартово произведение."""
        # Ограничиваем размер для читаемости
        a_list = sorted(list(self.set_a))[:4]
        b_list = sorted(list(self.set_b))[:4]
        
        result = [(a, b) for a in a_list for b in b_list]
        result_str = "{" + ", ".join([f"({a}, {b})" for a, b in result]) + "}"
        
        if len(self.set_a) > 4 or len(self.set_b) > 4:
            result_str += " ..."
        
        template = templates.get("cartesian_pairs", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=result_str))
        
        self.final_answer = f"|A × B| = {len(self.set_a)} × {len(self.set_b)} = {len(self.set_a) * len(self.set_b)}"
    
    def _solve_boolean_simplify(self, templates):
        """Упрощение логического выражения."""
        template = templates.get("boolean_law", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, law=self.law_name, result=self.simplified))
        
        self.final_answer = self.simplified
    
    def _solve_truth_table(self, templates):
        """Построение таблицы истинности."""
        if self.num_vars == 2:
            if self.language == "ru":
                header = "| A | B | Результат |"
                separator = "|---|---|-----------|"
                rows = [
                    "| 0 | 0 |     {}    |",
                    "| 0 | 1 |     {}    |",
                    "| 1 | 0 |     {}    |",
                    "| 1 | 1 |     {}    |",
                ]
            else:
                header = "| A | B | Result |"
                separator = "|---|---|--------|"
                rows = [
                    "| 0 | 0 |   {}   |",
                    "| 0 | 1 |   {}   |",
                    "| 1 | 0 |   {}   |",
                    "| 1 | 1 |   {}   |",
                ]
            
            # Вычисляем значения
            def eval_expr(a, b):
                if self.expression == "A ∧ B":
                    return int(a and b)
                elif self.expression == "A ∨ B":
                    return int(a or b)
                elif self.expression == "A → B":
                    return int((not a) or b)
                elif self.expression == "A ↔ B":
                    return int(a == b)
                elif self.expression == "¬A ∨ B":
                    return int((not a) or b)
                return 0
            
            values = [eval_expr(False, False), eval_expr(False, True),
                     eval_expr(True, False), eval_expr(True, True)]
            
            table = header + "\n" + separator + "\n"
            for row, val in zip(rows, values):
                table += row.format(val) + "\n"
            
            self.solution_steps.append(table)
        
        self.final_answer = "Таблица истинности построена" if self.language == "ru" else "Truth table constructed"
    
    def _solve_venn_problem(self, templates):
        """Задача на диаграмму Венна."""
        template = templates.get("venn_calculate", {}).get(self.language, "")
        
        a_total = self.only_a + self.both
        b_total = self.only_b + self.both
        
        if self.language == "ru":
            calc = f"Всего = {self.total}, знают англ. = {a_total}, знают франц. = {b_total}, оба = {self.both}"
            self.solution_steps.append(template.format(step=1, calculation=calc))
            self.solution_steps.append(template.format(
                step=2, calculation=f"Ни одного = {self.total} - {a_total} - {b_total} + {self.both} = {self.neither}"
            ))
        else:
            calc = f"Total = {self.total}, know English = {a_total}, know French = {b_total}, both = {self.both}"
            self.solution_steps.append(template.format(step=1, calculation=calc))
            self.solution_steps.append(template.format(
                step=2, calculation=f"Neither = {self.total} - {a_total} - {b_total} + {self.both} = {self.neither}"
            ))
        
        self.final_answer = str(self.neither)
    
    def get_task_type(self) -> str:
        return "set_logic"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу на множества и логику."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
