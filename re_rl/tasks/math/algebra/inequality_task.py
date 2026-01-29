# re_rl/tasks/inequality_task.py

"""
InequalityTask — задачи на неравенства.

Поддерживаемые типы:
- linear: линейные неравенства
- quadratic: квадратные неравенства
- rational: дробно-рациональные неравенства
- absolute: неравенства с модулем
- system: системы неравенств
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class InequalityTask(BaseMathTask):
    """Задачи на неравенства."""
    
    TASK_TYPES = [
        "linear", "quadratic", "rational", "absolute", "system"
    ]
    
    SIGNS = ["<", ">", "≤", "≥"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 5, "complexity": 1},
        2: {"max_coef": 10, "complexity": 1},
        3: {"max_coef": 15, "complexity": 2},
        4: {"max_coef": 20, "complexity": 2},
        5: {"max_coef": 25, "complexity": 3},
        6: {"max_coef": 30, "complexity": 3},
        7: {"max_coef": 40, "complexity": 4},
        8: {"max_coef": 50, "complexity": 4},
        9: {"max_coef": 75, "complexity": 5},
        10: {"max_coef": 100, "complexity": 5},
    }
    
    def __init__(
        self,
        task_type: str = "linear",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.kwargs = kwargs
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_coef = kwargs.get("max_coef", preset.get("max_coef", 25))
        self.complexity = kwargs.get("complexity", preset.get("complexity", 2))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _rand_coef(self, exclude_zero: bool = False) -> int:
        """Генерирует случайный коэффициент."""
        val = random.randint(-self.max_coef, self.max_coef)
        if exclude_zero:
            while val == 0:
                val = random.randint(-self.max_coef, self.max_coef)
        return val
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        self.sign = random.choice(self.SIGNS)
        
        if self.task_type == "linear":
            self.a = self._rand_coef(exclude_zero=True)
            self.b = self._rand_coef()
            self.c = self._rand_coef()
        
        elif self.task_type == "quadratic":
            self.a = self._rand_coef(exclude_zero=True)
            self.b = self._rand_coef()
            self.c = self._rand_coef()
            # Гарантируем действительные корни для интересного решения
            discriminant = self.b ** 2 - 4 * self.a * self.c
            while discriminant < 0:
                self.c = self._rand_coef()
                discriminant = self.b ** 2 - 4 * self.a * self.c
        
        elif self.task_type == "rational":
            # (ax + b) / (cx + d) > 0
            self.a = self._rand_coef(exclude_zero=True)
            self.b = self._rand_coef()
            self.c = self._rand_coef(exclude_zero=True)
            self.d = self._rand_coef()
            # Гарантируем разные корни
            while self.a * self.d == self.b * self.c:
                self.d = self._rand_coef()
        
        elif self.task_type == "absolute":
            self.a = self._rand_coef(exclude_zero=True)
            self.b = self._rand_coef()
            self.value = abs(self._rand_coef()) + 1  # Положительное значение
        
        elif self.task_type == "system":
            # Система двух линейных неравенств
            self.a1 = self._rand_coef(exclude_zero=True)
            self.b1 = self._rand_coef()
            self.c1 = self._rand_coef()
            self.sign1 = random.choice(self.SIGNS)
            
            self.a2 = self._rand_coef(exclude_zero=True)
            self.b2 = self._rand_coef()
            self.c2 = self._rand_coef()
            self.sign2 = random.choice(self.SIGNS)
    
    def _format_sign(self, sign: str) -> str:
        """Форматирует знак неравенства."""
        return sign
    
    def _format_linear_expr(self, a: int, b: int, var: str = "x") -> str:
        """Форматирует линейное выражение ax + b."""
        if a == 1:
            a_str = var
        elif a == -1:
            a_str = f"-{var}"
        else:
            a_str = f"{a}{var}"
        
        if b == 0:
            return a_str
        elif b > 0:
            return f"{a_str} + {b}"
        else:
            return f"{a_str} - {abs(b)}"
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("inequality", {}).get("problem", {})
        
        if self.task_type == "linear":
            template = templates.get("linear", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, sign=self.sign, c=self.c)
        
        elif self.task_type == "quadratic":
            template = templates.get("quadratic", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, c=self.c, sign=self.sign)
        
        elif self.task_type == "rational":
            template = templates.get("rational", {}).get(self.language, "")
            numerator = self._format_linear_expr(self.a, self.b)
            denominator = self._format_linear_expr(self.c, self.d)
            return template.format(numerator=numerator, denominator=denominator, sign=self.sign)
        
        elif self.task_type == "absolute":
            template = templates.get("absolute", {}).get(self.language, "")
            expression = self._format_linear_expr(self.a, self.b)
            return template.format(expression=expression, sign=self.sign, value=self.value)
        
        elif self.task_type == "system":
            template = templates.get("system", {}).get(self.language, "")
            ineq1 = f"{self.a1}x + {self.b1} {self.sign1} {self.c1}"
            ineq2 = f"{self.a2}x + {self.b2} {self.sign2} {self.c2}"
            return template.format(inequalities=f"{ineq1}\n{ineq2}")
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("inequality", {}).get("steps", {})
        
        if self.task_type == "linear":
            self._solve_linear(steps_templates)
        elif self.task_type == "quadratic":
            self._solve_quadratic(steps_templates)
        elif self.task_type == "rational":
            self._solve_rational(steps_templates)
        elif self.task_type == "absolute":
            self._solve_absolute(steps_templates)
        elif self.task_type == "system":
            self._solve_system(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _flip_sign(self, sign: str) -> str:
        """Меняет направление неравенства."""
        flip_map = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
        return flip_map.get(sign, sign)
    
    def _solve_linear(self, templates):
        """Решение линейного неравенства ax + b < c."""
        rhs = self.c - self.b
        
        template1 = templates.get("linear_solve", {}).get(self.language, "")
        self.solution_steps.append(template1.format(step=1, a=self.a, sign=self.sign, c=self.c, b=self.b, rhs=rhs))
        
        result = rhs / self.a
        
        if self.a > 0:
            template2 = templates.get("divide_positive", {}).get(self.language, "")
            self.solution_steps.append(template2.format(step=2, a=self.a, sign=self.sign, result=f"{result:.4f}"))
            final_sign = self.sign
        else:
            template2 = templates.get("divide_negative", {}).get(self.language, "")
            final_sign = self._flip_sign(self.sign)
            self.solution_steps.append(template2.format(step=2, a=self.a, new_sign=final_sign, result=f"{result:.4f}"))
        
        # Формируем ответ в интервальной записи
        result_val = result
        if final_sign == "<":
            answer = f"(-∞, {result_val:.4f})"
        elif final_sign == "≤":
            answer = f"(-∞, {result_val:.4f}]"
        elif final_sign == ">":
            answer = f"({result_val:.4f}, +∞)"
        else:  # ≥
            answer = f"[{result_val:.4f}, +∞)"
        
        self.final_answer = answer
    
    def _solve_quadratic(self, templates):
        """Решение квадратного неравенства."""
        discriminant = self.b ** 2 - 4 * self.a * self.c
        
        if discriminant > 0:
            x1 = (-self.b - math.sqrt(discriminant)) / (2 * self.a)
            x2 = (-self.b + math.sqrt(discriminant)) / (2 * self.a)
            if x1 > x2:
                x1, x2 = x2, x1
            
            template = templates.get("quadratic_roots", {}).get(self.language, "")
            self.solution_steps.append(template.format(step=1, x1=f"{x1:.4f}", x2=f"{x2:.4f}"))
            
            # Анализ знаков
            if self.a > 0:
                if self.sign in ["<", "≤"]:
                    bracket_left = "[" if self.sign == "≤" else "("
                    bracket_right = "]" if self.sign == "≤" else ")"
                    answer = f"{bracket_left}{x1:.4f}, {x2:.4f}{bracket_right}"
                else:
                    bracket_left = "[" if self.sign == "≥" else "("
                    bracket_right = "]" if self.sign == "≥" else ")"
                    answer = f"(-∞, {x1:.4f}{bracket_right} ∪ {bracket_left}{x2:.4f}, +∞)"
            else:
                if self.sign in ["<", "≤"]:
                    answer = f"(-∞, {x1:.4f}) ∪ ({x2:.4f}, +∞)"
                else:
                    answer = f"[{x1:.4f}, {x2:.4f}]"
        
        elif discriminant == 0:
            x = -self.b / (2 * self.a)
            answer = f"x = {x:.4f}" if self.sign in ["≤", "≥"] else "∅"
        
        else:
            if (self.a > 0 and self.sign in [">", "≥"]) or (self.a < 0 and self.sign in ["<", "≤"]):
                answer = "ℝ"
            else:
                answer = "∅"
        
        template2 = templates.get("sign_analysis", {}).get(self.language, "")
        self.solution_steps.append(template2.format(step=2, intervals=answer))
        
        self.final_answer = answer
    
    def _solve_rational(self, templates):
        """Решение дробно-рационального неравенства."""
        # Корни числителя и знаменателя
        x_num = -self.b / self.a if self.a != 0 else None
        x_den = -self.d / self.c if self.c != 0 else None
        
        template = templates.get("critical_points", {}).get(self.language, "")
        points_str = f"x = {x_num:.4f}, x = {x_den:.4f}" if x_num and x_den else "точки не определены"
        self.solution_steps.append(template.format(step=1, points=points_str))
        
        # Упрощённый анализ знаков
        if x_num and x_den:
            x_min, x_max = sorted([x_num, x_den])
            
            if self.sign in [">", "≥"]:
                # Положительное значение
                if (self.a > 0 and self.c > 0) or (self.a < 0 and self.c < 0):
                    answer = f"(-∞, {x_min:.4f}) ∪ ({x_max:.4f}, +∞)"
                else:
                    answer = f"({x_min:.4f}, {x_max:.4f})"
            else:
                if (self.a > 0 and self.c > 0) or (self.a < 0 and self.c < 0):
                    answer = f"({x_min:.4f}, {x_max:.4f})"
                else:
                    answer = f"(-∞, {x_min:.4f}) ∪ ({x_max:.4f}, +∞)"
        else:
            answer = "требуется дополнительный анализ"
        
        self.final_answer = answer
    
    def _solve_absolute(self, templates):
        """Решение неравенства с модулем."""
        expression = self._format_linear_expr(self.a, self.b)
        
        template = templates.get("absolute_split", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, expression=expression))
        
        # |ax + b| < c эквивалентно -c < ax + b < c
        # |ax + b| > c эквивалентно ax + b < -c или ax + b > c
        
        if self.sign in ["<", "≤"]:
            # -value < ax + b < value
            x1 = (-self.value - self.b) / self.a
            x2 = (self.value - self.b) / self.a
            if x1 > x2:
                x1, x2 = x2, x1
            
            bracket = "[]" if self.sign == "≤" else "()"
            answer = f"({x1:.4f}, {x2:.4f})" if self.sign == "<" else f"[{x1:.4f}, {x2:.4f}]"
        else:
            # ax + b < -value или ax + b > value
            x1 = (-self.value - self.b) / self.a
            x2 = (self.value - self.b) / self.a
            if x1 > x2:
                x1, x2 = x2, x1
            
            if self.sign == ">":
                answer = f"(-∞, {x1:.4f}) ∪ ({x2:.4f}, +∞)"
            else:
                answer = f"(-∞, {x1:.4f}] ∪ [{x2:.4f}, +∞)"
        
        self.final_answer = answer
    
    def _solve_system(self, templates):
        """Решение системы неравенств."""
        # Решаем каждое неравенство отдельно
        rhs1 = self.c1 - self.b1
        result1 = rhs1 / self.a1
        sign1 = self.sign1 if self.a1 > 0 else self._flip_sign(self.sign1)
        
        rhs2 = self.c2 - self.b2
        result2 = rhs2 / self.a2
        sign2 = self.sign2 if self.a2 > 0 else self._flip_sign(self.sign2)
        
        misc = PROMPT_TEMPLATES.get("inequality", {}).get("misc", {})
        
        step1 = misc.get("system_first_ineq", {}).get(self.language, "")
        self.solution_steps.append(step1.format(sign=sign1, value=f"{result1:.4f}"))
        
        step2 = misc.get("system_second_ineq", {}).get(self.language, "")
        self.solution_steps.append(step2.format(sign=sign2, value=f"{result2:.4f}"))
        
        # Находим пересечение
        # Упрощённая логика
        template = templates.get("system_intersection", {}).get(self.language, "")
        
        # Определяем границы
        left_bound = max(
            result1 if sign1 in [">", "≥"] else float("-inf"),
            result2 if sign2 in [">", "≥"] else float("-inf")
        )
        right_bound = min(
            result1 if sign1 in ["<", "≤"] else float("inf"),
            result2 if sign2 in ["<", "≤"] else float("inf")
        )
        
        if left_bound < right_bound:
            answer = f"({left_bound:.4f}, {right_bound:.4f})"
        elif left_bound == right_bound:
            answer = f"x = {left_bound:.4f}"
        else:
            answer = "∅"
        
        self.solution_steps.append(template.format(step=3, intersection=answer))
        
        self.final_answer = answer
    
    def get_task_type(self) -> str:
        return "inequality"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу на неравенства."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
