# re_rl/tasks/differential_equation_task.py

"""
DifferentialEquationTask — задачи на дифференциальные уравнения.

Поддерживаемые типы:
- separable: с разделяющимися переменными
- linear_first_order: линейные первого порядка
- homogeneous_second_order: однородные второго порядка
- exponential_growth: экспоненциальный рост/убывание
- cauchy_problem: задача Коши
"""

import random
import math
import sympy as sp
from typing import List, Dict, Any, ClassVar, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DifferentialEquationTask(BaseMathTask):
    """Генератор задач на дифференциальные уравнения."""
    
    TASK_TYPES = [
        "separable", "linear_first_order", "homogeneous_second_order",
        "exponential_growth", "cauchy_problem"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 3, "ode_order": 1, "simple": True},
        2: {"max_coef": 5, "ode_order": 1, "simple": True},
        3: {"max_coef": 5, "ode_order": 1, "simple": False},
        4: {"max_coef": 7, "ode_order": 1, "simple": False},
        5: {"max_coef": 10, "ode_order": 2, "simple": True},
        6: {"max_coef": 10, "ode_order": 2, "simple": False},
        7: {"max_coef": 15, "ode_order": 2, "simple": False},
        8: {"max_coef": 15, "ode_order": 2, "simple": False},
        9: {"max_coef": 20, "ode_order": 2, "simple": False},
        10: {"max_coef": 20, "ode_order": 2, "simple": False},
    }
    
    def __init__(
        self,
        task_type: str = "separable",
        coefficients: Dict[str, float] = None,
        initial_conditions: Dict[str, float] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.max_coef = preset.get("max_coef", 10)
        self.ode_order = preset.get("ode_order", 1)
        self.simple = preset.get("simple", True)
        
        # Генерируем коэффициенты
        self.coefficients = coefficients if coefficients else self._generate_coefficients()
        self.initial_conditions = initial_conditions
        
        # Генерируем начальные условия для задачи Коши
        if self.task_type == "cauchy_problem" and not self.initial_conditions:
            self.initial_conditions = {"y0": random.randint(1, 5), "x0": 0}
        
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_coefficients(self) -> Dict[str, float]:
        """Генерирует коэффициенты уравнения."""
        if self.task_type == "separable":
            return {
                "a": random.randint(1, self.max_coef),
                "b": random.randint(1, self.max_coef)
            }
        elif self.task_type == "linear_first_order":
            return {
                "p": random.randint(1, min(5, self.max_coef)),
                "q": random.randint(1, self.max_coef)
            }
        elif self.task_type == "homogeneous_second_order":
            # y'' + ay' + by = 0
            # Генерируем так, чтобы корни были простыми
            r1 = random.randint(-3, 3)
            r2 = random.randint(-3, 3)
            if r1 == r2:
                r2 += 1
            a = -(r1 + r2)  # сумма корней со знаком минус
            b = r1 * r2     # произведение корней
            return {"a": a, "b": b, "r1": r1, "r2": r2}
        elif self.task_type == "exponential_growth":
            return {"k": random.choice([1, 2, 3, -1, -2, -3])}
        else:  # cauchy_problem
            return {
                "a": random.randint(1, self.max_coef),
                "b": random.randint(1, self.max_coef)
            }
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        is_latex = self._output_format == "latex"
        templates = PROMPT_TEMPLATES.get("differential_equation", {}).get("problem", {})
        
        if self.task_type == "separable":
            a, b = self.coefficients["a"], self.coefficients["b"]
            if is_latex:
                eq = f"$\\frac{{dy}}{{dx}} = \\frac{{{a}x}}{{{b}y}}$"
            else:
                eq = f"dy/dx = {a}x / {b}y" if b != 1 else f"dy/dx = {a}x / y"
            template = templates.get("separable", {}).get(self.language, "")
            return template.format(equation=eq)
        
        elif self.task_type == "linear_first_order":
            p, q = self.coefficients["p"], self.coefficients["q"]
            if is_latex:
                eq = f"$y' + {p}y = {q}$"
            else:
                eq = f"y' + {p}y = {q}"
            template = templates.get("linear_first_order", {}).get(self.language, "")
            return template.format(equation=eq)
        
        elif self.task_type == "homogeneous_second_order":
            a, b = self.coefficients["a"], self.coefficients["b"]
            # Формируем строку уравнения
            terms = ["y''"]
            if a != 0:
                if a > 0:
                    terms.append(f" + {a}y'" if a != 1 else " + y'")
                else:
                    terms.append(f" - {-a}y'" if a != -1 else " - y'")
            if b != 0:
                if b > 0:
                    terms.append(f" + {b}y" if b != 1 else " + y")
                else:
                    terms.append(f" - {-b}y" if b != -1 else " - y")
            eq_str = "".join(terms) + " = 0"
            eq = f"${eq_str}$" if is_latex else eq_str
            template = templates.get("homogeneous_second_order", {}).get(self.language, "")
            return template.format(equation=eq)
        
        elif self.task_type == "exponential_growth":
            k = self.coefficients["k"]
            if is_latex:
                eq = f"$\\frac{{dy}}{{dx}} = {k}y$"
            else:
                eq = f"dy/dx = {k}y"
            # Шаблон использует {k}, но мы хотим использовать {equation}
            template = templates.get("exponential_growth", {}).get(self.language, "")
            return template.format(k=k)
        
        elif self.task_type == "cauchy_problem":
            a = self.coefficients["a"]
            x0 = self.initial_conditions['x0']
            y0 = self.initial_conditions['y0']
            if is_latex:
                eq = f"$\\frac{{dy}}{{dx}} = {a}y$"
                cond = f"$y({x0}) = {y0}$"
            else:
                eq = f"dy/dx = {a}y"
                cond = f"y({x0}) = {y0}"
            template = templates.get("cauchy_problem", {}).get(self.language, "")
            return template.format(equation=eq, conditions=cond)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("differential_equation", {}).get("steps", {})
        
        if self.task_type == "separable":
            self._solve_separable(templates)
        elif self.task_type == "linear_first_order":
            self._solve_linear_first_order(templates)
        elif self.task_type == "homogeneous_second_order":
            self._solve_homogeneous_second_order(templates)
        elif self.task_type == "exponential_growth":
            self._solve_exponential_growth(templates)
        elif self.task_type == "cauchy_problem":
            self._solve_cauchy(templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_separable(self, templates):
        """Уравнение с разделяющимися переменными."""
        a, b = self.coefficients["a"], self.coefficients["b"]
        
        # dy/dx = ax/by  =>  by dy = ax dx
        step1 = templates.get("separate_variables", {}).get(self.language, "")
        self.solution_steps.append(step1.format(separated=f"{b}y dy = {a}x dx"))
        
        # Интегрируем
        step2 = templates.get("integrate_both", {}).get(self.language, "")
        self.solution_steps.append(step2.format(left=f"{b}y dy", right=f"{a}x dx"))
        
        # Результат: by²/2 = ax²/2 + C  =>  y² = (a/b)x² + C
        ratio = a / b
        step3 = templates.get("general_solution", {}).get(self.language, "")
        self.solution_steps.append(step3.format(step=3, solution=f"y² = {ratio:.4g}x² + C"))
        
        self.final_answer = f"y² = {ratio:.4g}x² + C"
    
    def _solve_linear_first_order(self, templates):
        """Линейное ДУ первого порядка: y' + py = q."""
        p, q = self.coefficients["p"], self.coefficients["q"]
        
        # Интегрирующий множитель: μ = e^(px)
        # Общее решение: y = e^(-px) * (∫q*e^(px)dx + C)
        # Для постоянных p и q: y = q/p + Ce^(-px)
        
        y_particular = q / p
        
        step1 = templates.get("general_solution", {}).get(self.language, "")
        solution = f"y = {y_particular:.4g} + Ce^(-{p}x)"
        self.solution_steps.append(step1.format(step=1, solution=solution))
        
        self.final_answer = solution
    
    def _solve_homogeneous_second_order(self, templates):
        """Однородное ДУ второго порядка: y'' + ay' + by = 0."""
        a, b = self.coefficients["a"], self.coefficients["b"]
        r1, r2 = self.coefficients["r1"], self.coefficients["r2"]
        
        # Характеристическое уравнение: r² + ar + b = 0
        char_eq = f"r² + {a}r + {b} = 0" if a >= 0 else f"r² - {-a}r + {b} = 0"
        step1 = templates.get("characteristic_equation", {}).get(self.language, "")
        self.solution_steps.append(step1.format(char_eq=char_eq))
        
        # Корни
        step2 = templates.get("find_roots", {}).get(self.language, "")
        self.solution_steps.append(step2.format(roots=f"r₁ = {r1}, r₂ = {r2}"))
        
        # Общее решение
        if r1 != r2:
            solution = f"y = C₁e^({r1}x) + C₂e^({r2}x)"
        else:
            solution = f"y = (C₁ + C₂x)e^({r1}x)"
        
        step3 = templates.get("general_solution", {}).get(self.language, "")
        self.solution_steps.append(step3.format(step=3, solution=solution))
        
        self.final_answer = solution
    
    def _solve_exponential_growth(self, templates):
        """Экспоненциальный рост: dy/dx = ky."""
        k = self.coefficients["k"]
        
        # Общее решение: y = Ce^(kx)
        step1 = templates.get("general_solution", {}).get(self.language, "")
        solution = f"y = Ce^({k}x)"
        self.solution_steps.append(step1.format(step=1, solution=solution))
        
        self.final_answer = solution
    
    def _solve_cauchy(self, templates):
        """Задача Коши: dy/dx = ay, y(x0) = y0."""
        a = self.coefficients["a"]
        y0 = self.initial_conditions["y0"]
        x0 = self.initial_conditions["x0"]
        
        # Общее решение: y = Ce^(ax)
        # Из y(x0) = y0: C = y0 * e^(-a*x0)
        
        step1 = templates.get("general_solution", {}).get(self.language, "")
        self.solution_steps.append(step1.format(step=1, solution=f"y = Ce^({a}x)"))
        
        # Применяем начальные условия
        C = y0 * math.exp(-a * x0)
        step2 = templates.get("apply_initial", {}).get(self.language, "")
        self.solution_steps.append(step2.format(step=2, conditions=f"C = {C:.4g}"))
        
        # Частное решение
        if x0 == 0:
            solution = f"y = {y0}e^({a}x)"
        else:
            solution = f"y = {C:.4g}e^({a}x)"
        
        step3 = templates.get("particular_solution", {}).get(self.language, "")
        self.solution_steps.append(step3.format(step=3, solution=solution))
        
        self.final_answer = solution
    
    def get_task_type(self) -> str:
        return "differential_equation"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text"
    ):
        """Генерирует случайную задачу на ДУ."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format
        )
