# re_rl/tasks/limits_task.py

"""
LimitsTask — задачи на пределы.

Поддерживаемые типы:
- polynomial: пределы полиномов
- rational: пределы рациональных функций
- infinity: пределы на бесконечности
- indeterminate: неопределённости (0/0, ∞/∞)
- sequence: пределы последовательностей
- special: замечательные пределы
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass
import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class LimitsTask(BaseMathTask):
    """Задачи на пределы."""
    
    TASK_TYPES = [
        "polynomial", "rational", "infinity", "indeterminate", "sequence", "special"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_degree": 2, "max_coef": 5},
        2: {"max_degree": 2, "max_coef": 10},
        3: {"max_degree": 3, "max_coef": 10},
        4: {"max_degree": 3, "max_coef": 15},
        5: {"max_degree": 4, "max_coef": 15},
        6: {"max_degree": 4, "max_coef": 20},
        7: {"max_degree": 5, "max_coef": 20},
        8: {"max_degree": 5, "max_coef": 25},
        9: {"max_degree": 6, "max_coef": 30},
        10: {"max_degree": 6, "max_coef": 50},
    }
    
    def __init__(
        self,
        task_type: str = "polynomial",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.kwargs = kwargs
        self._output_format = output_format
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_degree = kwargs.get("max_degree", preset.get("max_degree", 4))
        self.max_coef = kwargs.get("max_coef", preset.get("max_coef", 15))
        
        # Символ x
        self.x = sp.Symbol('x')
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _rand_coef(self) -> int:
        """Генерирует случайный коэффициент."""
        return random.randint(-self.max_coef, self.max_coef)
    
    def _generate_polynomial(self, degree: int) -> sp.Expr:
        """Генерирует случайный полином."""
        coeffs = [self._rand_coef() for _ in range(degree + 1)]
        # Гарантируем ненулевой старший коэффициент
        while coeffs[-1] == 0:
            coeffs[-1] = random.choice([-1, 1]) * random.randint(1, self.max_coef)
        
        return sum(c * self.x**i for i, c in enumerate(coeffs))
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type == "polynomial":
            self.point = self._rand_coef()
            degree = random.randint(1, self.max_degree)
            self.expression = self._generate_polynomial(degree)
        
        elif self.task_type == "rational":
            self.point = random.choice([0, 1, 2, -1, -2])
            deg_num = random.randint(1, self.max_degree)
            deg_den = random.randint(1, self.max_degree)
            self.numerator = self._generate_polynomial(deg_num)
            self.denominator = self._generate_polynomial(deg_den)
            # Убеждаемся, что знаменатель не 0 в точке
            while self.denominator.subs(self.x, self.point) == 0:
                self.denominator = self._generate_polynomial(deg_den)
            self.expression = self.numerator / self.denominator
        
        elif self.task_type == "infinity":
            deg_num = random.randint(1, self.max_degree)
            deg_den = random.randint(1, self.max_degree)
            self.numerator = self._generate_polynomial(deg_num)
            self.denominator = self._generate_polynomial(deg_den)
            self.expression = self.numerator / self.denominator
        
        elif self.task_type == "indeterminate":
            self._generate_indeterminate()
        
        elif self.task_type == "sequence":
            self._generate_sequence()
        
        elif self.task_type == "special":
            self._generate_special()
    
    def _generate_indeterminate(self):
        """Генерирует неопределённость 0/0."""
        self.point = random.choice([0, 1, -1, 2])
        # Создаём функцию с общим множителем (x - point)
        factor = self.x - self.point
        
        # Числитель и знаменатель с общим множителем
        num_extra = self._generate_polynomial(random.randint(1, 2))
        den_extra = self._generate_polynomial(random.randint(1, 2))
        
        # Убеждаемся, что дополнительные части не обнуляются в точке
        while num_extra.subs(self.x, self.point) == 0:
            num_extra = self._generate_polynomial(random.randint(1, 2))
        while den_extra.subs(self.x, self.point) == 0:
            den_extra = self._generate_polynomial(random.randint(1, 2))
        
        self.numerator = sp.expand(factor * num_extra)
        self.denominator = sp.expand(factor * den_extra)
        self.expression = self.numerator / self.denominator
        self.indeterminate_type = "0/0"
    
    def _generate_sequence(self):
        """Генерирует предел последовательности."""
        n = sp.Symbol('n')
        self.n_symbol = n
        
        sequence_types = [
            (n + 1) / n,  # -> 1
            (n**2 + n) / (n**2),  # -> 1
            (2*n + 1) / (3*n + 2),  # -> 2/3
            n / (n + 1),  # -> 1
            (1 + 1/n)**n,  # -> e (но сложно вычислить символьно)
        ]
        
        self.sequence_expr = random.choice(sequence_types[:3])
        self.expression = self.sequence_expr
    
    def _generate_special(self):
        """Генерирует замечательный предел."""
        special_limits = [
            ("sin(x)/x", 0, 1),
            ("(1 - cos(x))/x²", 0, sp.Rational(1, 2)),
            ("tan(x)/x", 0, 1),
            ("(e^x - 1)/x", 0, 1),
            ("ln(1 + x)/x", 0, 1),
        ]
        
        self.special_type, self.point, self.expected_result = random.choice(special_limits)
        self.expression = sp.sympify(self.special_type)
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        is_latex = self._output_format == "latex"
        templates = PROMPT_TEMPLATES.get("limits", {}).get("problem", {})
        
        # Форматируем выражение предела
        if is_latex:
            expr_latex = sp.latex(self.expression)
            if self.task_type == "infinity":
                limit_expr = f"$\\lim_{{x \\to \\infty}} {expr_latex}$"
            elif self.task_type == "sequence":
                limit_expr = f"$\\lim_{{n \\to \\infty}} {expr_latex}$"
            else:
                limit_expr = f"$\\lim_{{x \\to {self.point}}} {expr_latex}$"
        else:
            expr_str = sp.pretty(self.expression)
            if self.task_type == "infinity":
                limit_expr = f"lim(x→∞) ({expr_str})"
            elif self.task_type == "sequence":
                limit_expr = f"lim(n→∞) {expr_str}"
            else:
                limit_expr = f"lim(x→{self.point}) ({expr_str})"
        
        # Используем шаблоны
        template = templates.get(self.task_type, {}).get(self.language, "")
        
        if self.task_type == "indeterminate":
            return template.format(limit_expression=limit_expr, type=self.indeterminate_type)
        else:
            return template.format(limit_expression=limit_expr)
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("limits", {}).get("steps", {})
        
        if self.task_type == "polynomial":
            self._solve_polynomial(steps_templates)
        elif self.task_type == "rational":
            self._solve_rational(steps_templates)
        elif self.task_type == "infinity":
            self._solve_infinity(steps_templates)
        elif self.task_type == "indeterminate":
            self._solve_indeterminate(steps_templates)
        elif self.task_type == "sequence":
            self._solve_sequence(steps_templates)
        elif self.task_type == "special":
            self._solve_special(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_polynomial(self, templates):
        """Предел полинома - прямая подстановка."""
        result = self.expression.subs(self.x, self.point)
        
        template = templates.get("direct_substitution", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, point=self.point, expression=sp.pretty(self.expression), result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_rational(self, templates):
        """Предел рациональной функции."""
        result = sp.limit(self.expression, self.x, self.point)
        
        template = templates.get("direct_substitution", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, point=self.point, expression=sp.pretty(self.expression), result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_infinity(self, templates):
        """Предел на бесконечности."""
        result = sp.limit(self.expression, self.x, sp.oo)
        
        # Определяем степени
        num_degree = sp.degree(self.numerator, self.x)
        den_degree = sp.degree(self.denominator, self.x)
        
        template = templates.get("divide_highest_power", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, power=max(num_degree, den_degree), expression=sp.pretty(self.expression)
        ))
        
        if num_degree > den_degree:
            limit_result = "±∞"
        elif num_degree < den_degree:
            limit_result = "0"
        else:
            # Отношение старших коэффициентов
            limit_result = str(result)
        
        self.final_answer = str(result)
    
    def _solve_indeterminate(self, templates):
        """Раскрытие неопределённости."""
        template1 = templates.get("indeterminate_found", {}).get(self.language, "")
        self.solution_steps.append(template1.format(step=1, type=self.indeterminate_type))
        
        # Факторизуем и сокращаем
        template2 = templates.get("factorize", {}).get(self.language, "")
        factored_num = sp.factor(self.numerator)
        factored_den = sp.factor(self.denominator)
        self.solution_steps.append(template2.format(
            step=2, factorization=f"({sp.pretty(factored_num)}) / ({sp.pretty(factored_den)})"
        ))
        
        # Вычисляем предел
        result = sp.limit(self.expression, self.x, self.point)
        
        template3 = templates.get("simplify", {}).get(self.language, "")
        self.solution_steps.append(template3.format(step=3, simplified=str(result)))
        
        self.final_answer = str(result)
    
    def _solve_sequence(self, templates):
        """Предел последовательности."""
        n = self.n_symbol
        result = sp.limit(self.expression, n, sp.oo)
        
        template = templates.get("divide_highest_power", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, power="n", expression=sp.pretty(self.expression)
        ))
        
        self.final_answer = str(result)
    
    def _solve_special(self, templates):
        """Замечательный предел."""
        template = templates.get("remarkable_limit", {}).get(self.language, "")
        
        remarkable_limits = PROMPT_TEMPLATES.get("limits", {}).get("remarkable_limits", {}).get(self.language, {})
        
        if "sin" in self.special_type:
            formula = remarkable_limits.get("sin_x_over_x", "lim sin(x)/x = 1")
        elif "e^" in self.special_type:
            formula = remarkable_limits.get("e_x_minus_one", "lim (e^x - 1)/x = 1")
        elif "ln" in self.special_type:
            formula = remarkable_limits.get("ln_one_plus_x", "lim ln(1+x)/x = 1")
        else:
            formula = "Замечательный предел"
        
        self.solution_steps.append(template.format(step=1, limit_formula=formula))
        
        self.final_answer = str(self.expected_result)
    
    def get_task_type(self) -> str:
        return "limits"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text"
    ):
        """Генерирует случайную задачу на пределы."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format
        )
