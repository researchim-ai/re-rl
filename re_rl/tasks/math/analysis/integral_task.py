# re_rl/tasks/integral_task.py

"""
IntegralTask — задачи на интегрирование.

Поддерживаемые типы:
- indefinite_polynomial: неопределённый интеграл от многочлена
- definite_polynomial: определённый интеграл от многочлена
- indefinite_trig: неопределённый интеграл от тригонометрии
- definite_trig: определённый интеграл от тригонометрии
- area: площадь под кривой
"""

import random
import math
from typing import List, Dict, Any, ClassVar, Tuple
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

try:
    import sympy as sp
    from sympy import symbols, integrate, sin, cos, exp, log, sqrt, pi
    from sympy import Rational, simplify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class IntegralTask(BaseMathTask):
    """Генератор задач на интегрирование."""
    
    TASK_TYPES = [
        "indefinite_polynomial", "definite_polynomial",
        "indefinite_trig", "definite_trig", "area"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 1, "max_coef": 5, "terms": 2},
        2: {"degree": 2, "max_coef": 5, "terms": 2},
        3: {"degree": 2, "max_coef": 10, "terms": 3},
        4: {"degree": 3, "max_coef": 10, "terms": 3},
        5: {"degree": 3, "max_coef": 10, "terms": 4},
        6: {"degree": 4, "max_coef": 15, "terms": 4},
        7: {"degree": 4, "max_coef": 15, "terms": 5},
        8: {"degree": 5, "max_coef": 20, "terms": 5},
        9: {"degree": 5, "max_coef": 20, "terms": 6},
        10: {"degree": 6, "max_coef": 25, "terms": 6},
    }
    
    def __init__(
        self,
        task_type: str = "indefinite_polynomial",
        coefficients: List[int] = None,
        lower_bound: float = None,
        upper_bound: float = None,
        trig_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.degree = preset.get("degree", 3)
        self.max_coef = preset.get("max_coef", 10)
        self.num_terms = preset.get("terms", 4)
        
        # Генерируем коэффициенты
        self.coefficients = coefficients if coefficients else self._generate_coefficients()
        
        # Границы для определённого интеграла
        self.lower_bound = lower_bound if lower_bound is not None else random.randint(0, 3)
        self.upper_bound = upper_bound if upper_bound is not None else random.randint(self.lower_bound + 1, self.lower_bound + 5)
        
        # Тип тригонометрии
        self.trig_type = trig_type or random.choice(["sin", "cos"])
        self.trig_coef = random.randint(1, 3)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _generate_coefficients(self) -> List[int]:
        """Генерирует коэффициенты многочлена."""
        # [a_n, a_{n-1}, ..., a_1, a_0]
        coeffs = []
        for i in range(self.num_terms):
            coef = random.randint(-self.max_coef, self.max_coef)
            if coef == 0:
                coef = random.choice([-1, 1]) * random.randint(1, self.max_coef)
            coeffs.append(coef)
        return coeffs
    
    def _poly_to_str(self, coeffs: List[int], powers: List[int] = None) -> str:
        """Преобразует коэффициенты в строку многочлена."""
        if powers is None:
            powers = list(range(len(coeffs) - 1, -1, -1))
        
        terms = []
        for i, (coef, power) in enumerate(zip(coeffs, powers)):
            if coef == 0:
                continue
            
            # Знак
            if i == 0:
                sign = "" if coef > 0 else "-"
            else:
                sign = " + " if coef > 0 else " - "
            
            abs_coef = abs(coef)
            
            # Формат члена
            if power == 0:
                term = f"{abs_coef}"
            elif power == 1:
                term = f"{abs_coef}x" if abs_coef != 1 else "x"
            else:
                term = f"{abs_coef}x^{power}" if abs_coef != 1 else f"x^{power}"
            
            terms.append(f"{sign}{term}")
        
        return "".join(terms) if terms else "0"
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("integral", {}).get("problem", {})
        
        if self.task_type == "indefinite_polynomial":
            powers = list(range(len(self.coefficients) - 1, -1, -1))
            expr = self._poly_to_str(self.coefficients, powers)
            template = templates.get("indefinite_polynomial", {}).get(self.language, "")
            return template.format(expression=expr)
        
        elif self.task_type == "definite_polynomial":
            powers = list(range(len(self.coefficients) - 1, -1, -1))
            expr = self._poly_to_str(self.coefficients, powers)
            template = templates.get("definite_polynomial", {}).get(self.language, "")
            return template.format(a=self.lower_bound, b=self.upper_bound, expression=expr)
        
        elif self.task_type == "indefinite_trig":
            expr = f"{self.trig_coef}{self.trig_type}(x)" if self.trig_coef != 1 else f"{self.trig_type}(x)"
            template = templates.get("indefinite_trig", {}).get(self.language, "")
            return template.format(expression=expr)
        
        elif self.task_type == "definite_trig":
            expr = f"{self.trig_coef}{self.trig_type}(x)" if self.trig_coef != 1 else f"{self.trig_type}(x)"
            template = templates.get("definite_trig", {}).get(self.language, "")
            return template.format(a=0, b="π", expression=expr)
        
        elif self.task_type == "area":
            powers = list(range(len(self.coefficients) - 1, -1, -1))
            expr = self._poly_to_str(self.coefficients, powers)
            template = templates.get("area", {}).get(self.language, "")
            return template.format(expression=expr, a=self.lower_bound, b=self.upper_bound)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("integral", {}).get("steps", {})
        
        if self.task_type == "indefinite_polynomial":
            self._solve_indefinite_polynomial(templates)
        elif self.task_type == "definite_polynomial":
            self._solve_definite_polynomial(templates)
        elif self.task_type == "indefinite_trig":
            self._solve_indefinite_trig(templates)
        elif self.task_type == "definite_trig":
            self._solve_definite_trig(templates)
        elif self.task_type == "area":
            self._solve_area(templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_indefinite_polynomial(self, templates):
        """Неопределённый интеграл от многочлена."""
        # Показываем правило степени
        step1 = templates.get("power_rule", {}).get(self.language, "")
        self.solution_steps.append(step1.format(step=1))
        
        # Интегрируем каждый член
        result_terms = []
        powers = list(range(len(self.coefficients) - 1, -1, -1))
        step = 2
        
        for coef, power in zip(self.coefficients, powers):
            if coef == 0:
                continue
            
            new_power = power + 1
            new_coef = coef / new_power
            
            # Форматируем результат
            if new_power == 1:
                term = f"{new_coef:.4g}x" if abs(new_coef) != 1 else "x"
            else:
                term = f"{new_coef:.4g}x^{new_power}" if abs(new_coef) != 1 else f"x^{new_power}"
            
            if new_coef < 0:
                term = f"({term})"
            
            result_terms.append((new_coef, new_power))
            
            step_template = templates.get("apply_power", {}).get(self.language, "")
            self.solution_steps.append(step_template.format(
                step=step, coef=coef, n=power, new_n=new_power, 
                result=f"{new_coef:.4g}x^{new_power}"
            ))
            step += 1
        
        # Собираем результат
        result_str = self._format_integrated_result(result_terms)
        
        combine_template = templates.get("combine_terms", {}).get(self.language, "")
        self.solution_steps.append(combine_template.format(step=step, result=result_str))
        
        self.final_answer = f"{result_str} + C"
    
    def _solve_definite_polynomial(self, templates):
        """Определённый интеграл от многочлена."""
        # Сначала находим первообразную
        result_terms = []
        powers = list(range(len(self.coefficients) - 1, -1, -1))
        
        for coef, power in zip(self.coefficients, powers):
            if coef == 0:
                continue
            new_power = power + 1
            new_coef = coef / new_power
            result_terms.append((new_coef, new_power))
        
        # Вычисляем F(b) и F(a)
        def evaluate(x):
            return sum(coef * (x ** power) for coef, power in result_terms)
        
        fb = evaluate(self.upper_bound)
        fa = evaluate(self.lower_bound)
        result = fb - fa
        
        step_template = templates.get("evaluate_definite", {}).get(self.language, "")
        self.solution_steps.append(step_template.format(
            step=1, a=self.lower_bound, b=self.upper_bound,
            fa=f"{fa:.4f}", fb=f"{fb:.4f}", result=f"{result:.4f}"
        ))
        
        self.final_answer = f"{result:.4f}"
    
    def _solve_indefinite_trig(self, templates):
        """Неопределённый интеграл от тригонометрии."""
        if self.trig_type == "sin":
            result = f"-{self.trig_coef}cos(x)" if self.trig_coef != 1 else "-cos(x)"
            func = f"{self.trig_coef}sin(x)" if self.trig_coef != 1 else "sin(x)"
        else:  # cos
            result = f"{self.trig_coef}sin(x)" if self.trig_coef != 1 else "sin(x)"
            func = f"{self.trig_coef}cos(x)" if self.trig_coef != 1 else "cos(x)"
        
        step_template = templates.get("trig_integral", {}).get(self.language, "")
        self.solution_steps.append(step_template.format(step=1, func=func, result=result))
        
        self.final_answer = f"{result} + C"
    
    def _solve_definite_trig(self, templates):
        """Определённый интеграл от тригонометрии от 0 до π."""
        if self.trig_type == "sin":
            # ∫sin(x)dx от 0 до π = [-cos(x)] от 0 до π = -cos(π) + cos(0) = 1 + 1 = 2
            result = 2 * self.trig_coef
        else:  # cos
            # ∫cos(x)dx от 0 до π = [sin(x)] от 0 до π = sin(π) - sin(0) = 0
            result = 0
        
        step_template = templates.get("evaluate_definite", {}).get(self.language, "")
        self.solution_steps.append(step_template.format(
            step=1, a=0, b="π", fa="...", fb="...", result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_area(self, templates):
        """Площадь под кривой."""
        # То же, что и определённый интеграл
        self._solve_definite_polynomial(templates)
        
        # Берём модуль для площади
        try:
            area = abs(float(self.final_answer))
            self.final_answer = f"{area:.4f}"
        except:
            pass
    
    def _format_integrated_result(self, terms: List[Tuple[float, int]]) -> str:
        """Форматирует результат интегрирования."""
        parts = []
        for i, (coef, power) in enumerate(terms):
            if abs(coef) < 0.0001:
                continue
            
            if i == 0:
                sign = "" if coef >= 0 else "-"
            else:
                sign = " + " if coef >= 0 else " - "
            
            abs_coef = abs(coef)
            
            if power == 1:
                term = f"{abs_coef:.4g}x" if abs_coef != 1 else "x"
            else:
                term = f"{abs_coef:.4g}x^{power}" if abs_coef != 1 else f"x^{power}"
            
            parts.append(f"{sign}{term}")
        
        return "".join(parts) if parts else "0"
    
    def get_task_type(self) -> str:
        return "integral"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу на интегрирование."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
