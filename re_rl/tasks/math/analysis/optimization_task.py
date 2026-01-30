# re_rl/tasks/optimization_task.py

"""
OptimizationTask — задачи на оптимизацию.

Поддерживаемые типы:
- find_extremum: поиск экстремумов функции
- max_min_interval: max/min на отрезке
- linear_programming: линейное программирование
- word_problem: текстовые задачи на оптимизацию
"""

import random
import math
import sympy as sp
from typing import List, Dict, Any, ClassVar, Tuple, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class OptimizationTask(BaseMathTask):
    """Генератор задач на оптимизацию."""
    
    TASK_TYPES = [
        "find_extremum", "max_min_interval", "linear_programming"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 2, "max_coef": 5, "lp_vars": 2, "lp_constraints": 2},
        2: {"degree": 2, "max_coef": 10, "lp_vars": 2, "lp_constraints": 2},
        3: {"degree": 3, "max_coef": 10, "lp_vars": 2, "lp_constraints": 3},
        4: {"degree": 3, "max_coef": 15, "lp_vars": 2, "lp_constraints": 3},
        5: {"degree": 3, "max_coef": 15, "lp_vars": 2, "lp_constraints": 3},
        6: {"degree": 4, "max_coef": 20, "lp_vars": 2, "lp_constraints": 4},
        7: {"degree": 4, "max_coef": 20, "lp_vars": 2, "lp_constraints": 4},
        8: {"degree": 4, "max_coef": 25, "lp_vars": 3, "lp_constraints": 4},
        9: {"degree": 5, "max_coef": 25, "lp_vars": 3, "lp_constraints": 5},
        10: {"degree": 5, "max_coef": 30, "lp_vars": 3, "lp_constraints": 5},
    }
    
    def __init__(
        self,
        task_type: str = "find_extremum",
        coefficients: List[float] = None,
        interval: Tuple[float, float] = None,
        lp_objective: List[float] = None,
        lp_constraints: List[Tuple[List[float], float]] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.degree = preset.get("degree", 3)
        self.max_coef = preset.get("max_coef", 15)
        self.lp_vars = preset.get("lp_vars", 2)
        self.lp_constraints_count = preset.get("lp_constraints", 3)
        
        # Генерируем данные
        self.coefficients = coefficients if coefficients else self._generate_poly_coefficients()
        self.interval = interval if interval else self._generate_interval()
        
        # Для линейного программирования
        self.lp_objective = lp_objective
        self.lp_constraints = lp_constraints
        if self.task_type == "linear_programming":
            self._generate_lp_problem()
        
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _generate_poly_coefficients(self) -> List[float]:
        """Генерирует коэффициенты многочлена с хорошими экстремумами."""
        if self.degree == 2:
            # ax² + bx + c с вершиной в разумной точке
            a = random.choice([-1, 1]) * random.randint(1, 3)
            vertex_x = random.randint(-5, 5)
            vertex_y = random.randint(-10, 10)
            b = -2 * a * vertex_x
            c = a * vertex_x ** 2 + vertex_y
            return [a, b, c]
        else:
            # Для кубических и выше - простые коэффициенты
            coeffs = [random.randint(-self.max_coef, self.max_coef) for _ in range(self.degree + 1)]
            if coeffs[0] == 0:
                coeffs[0] = random.choice([-1, 1])
            return coeffs
    
    def _generate_interval(self) -> Tuple[float, float]:
        """Генерирует интервал."""
        a = random.randint(-5, 0)
        b = random.randint(a + 2, a + 8)
        return (a, b)
    
    def _generate_lp_problem(self):
        """Генерирует задачу линейного программирования."""
        if self.lp_objective is None:
            self.lp_objective = [random.randint(1, 10) for _ in range(self.lp_vars)]
        
        if self.lp_constraints is None:
            self.lp_constraints = []
            for _ in range(self.lp_constraints_count):
                coeffs = [random.randint(1, 5) for _ in range(self.lp_vars)]
                rhs = random.randint(10, 30)
                self.lp_constraints.append((coeffs, rhs))
            
            # Добавляем x >= 0, y >= 0 неявно
    
    def _poly_to_str(self, coeffs: List[float]) -> str:
        """Преобразует коэффициенты в строку."""
        terms = []
        n = len(coeffs) - 1
        
        for i, coef in enumerate(coeffs):
            if coef == 0:
                continue
            
            power = n - i
            
            if i == 0:
                sign = "" if coef > 0 else "-"
            else:
                sign = " + " if coef > 0 else " - "
            
            abs_coef = abs(coef)
            
            if power == 0:
                term = f"{abs_coef}"
            elif power == 1:
                term = f"{abs_coef}x" if abs_coef != 1 else "x"
            else:
                term = f"{abs_coef}x^{power}" if abs_coef != 1 else f"x^{power}"
            
            terms.append(f"{sign}{term}")
        
        return "".join(terms) if terms else "0"
    
    def _poly_to_latex(self, coeffs: List[float]) -> str:
        """Преобразует коэффициенты в LaTeX строку."""
        x = sp.Symbol('x')
        n = len(coeffs) - 1
        poly = sum(c * x**(n-i) for i, c in enumerate(coeffs))
        return sp.latex(poly)
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        is_latex = self._output_format == "latex"
        templates = PROMPT_TEMPLATES.get("optimization", {}).get("problem", {})
        on_interval = PROMPT_TEMPLATES["default"]["on_interval"][self.language]
        subject_to = PROMPT_TEMPLATES["default"]["subject_to"][self.language]
        
        if self.task_type == "find_extremum":
            if is_latex:
                expr_latex = self._poly_to_latex(self.coefficients)
                func_expr = f"$f(x) = {expr_latex}$"
            else:
                expr = self._poly_to_str(self.coefficients)
                func_expr = f"f(x) = {expr}"
            template = templates.get("find_extremum", {}).get(self.language, "")
            return template.format(function_expression=func_expr)
        
        elif self.task_type == "max_min_interval":
            if is_latex:
                expr_latex = self._poly_to_latex(self.coefficients)
                func_expr = f"$f(x) = {expr_latex}$ {on_interval} $[{self.interval[0]}, {self.interval[1]}]$"
            else:
                expr = self._poly_to_str(self.coefficients)
                func_expr = f"f(x) = {expr} {on_interval} [{self.interval[0]}, {self.interval[1]}]"
            template = templates.get("max_min_interval", {}).get(self.language, "")
            return template.format(function_expression=func_expr)
        
        elif self.task_type == "linear_programming":
            var_names = ["x", "y", "z"][:self.lp_vars]
            
            if is_latex:
                obj_terms = [f"{c}{v}" for c, v in zip(self.lp_objective, var_names)]
                objective = " + ".join(obj_terms)
                constraints_latex = []
                for coeffs, rhs in self.lp_constraints:
                    terms = [f"{c}{v}" for c, v in zip(coeffs, var_names)]
                    constraints_latex.append(" + ".join(terms) + f" \\leq {rhs}")
                for v in var_names:
                    constraints_latex.append(f"{v} \\geq 0")
                lp_expr = f"$\\max ({objective})$, {subject_to} ${', '.join(constraints_latex)}$"
            else:
                obj_terms = [f"{c}{v}" for c, v in zip(self.lp_objective, var_names)]
                objective = " + ".join(obj_terms)
                constraints_str = []
                for coeffs, rhs in self.lp_constraints:
                    terms = [f"{c}{v}" for c, v in zip(coeffs, var_names)]
                    constraints_str.append(" + ".join(terms) + f" ≤ {rhs}")
                for v in var_names:
                    constraints_str.append(f"{v} ≥ 0")
                lp_expr = f"max ({objective}), {subject_to}: {', '.join(constraints_str)}"
            
            template = templates.get("linear_programming", {}).get(self.language, "")
            return template.format(lp_expression=lp_expr)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("optimization", {}).get("steps", {})
        types = PROMPT_TEMPLATES.get("optimization", {}).get("types", {})
        
        if self.task_type == "find_extremum":
            self._solve_find_extremum(templates, types)
        elif self.task_type == "max_min_interval":
            self._solve_max_min_interval(templates, types)
        elif self.task_type == "linear_programming":
            self._solve_linear_programming(templates)
    
    def _derivative(self, coeffs: List[float]) -> List[float]:
        """Вычисляет производную многочлена."""
        n = len(coeffs) - 1
        if n == 0:
            return [0]
        return [coeffs[i] * (n - i) for i in range(n)]
    
    def _eval_poly(self, coeffs: List[float], x: float) -> float:
        """Вычисляет значение многочлена."""
        result = 0
        n = len(coeffs) - 1
        for i, c in enumerate(coeffs):
            result += c * (x ** (n - i))
        return result
    
    def _solve_find_extremum(self, templates, types):
        """Поиск экстремумов."""
        # Находим производную
        deriv = self._derivative(self.coefficients)
        deriv_str = self._poly_to_str(deriv)
        
        step1 = templates.get("find_derivative", {}).get(self.language, "")
        self.solution_steps.append(step1.format(derivative=deriv_str))
        
        # Для квадратного многочлена: критическая точка x = -b/(2a)
        if len(self.coefficients) == 3:
            a, b, c = self.coefficients
            critical_x = -b / (2 * a)
            
            step2 = templates.get("critical_points", {}).get(self.language, "")
            self.solution_steps.append(step2.format(points=f"x = {critical_x:.4f}"))
            
            # Вторая производная = 2a
            second_deriv = 2 * a
            step3 = templates.get("second_derivative", {}).get(self.language, "")
            self.solution_steps.append(step3.format(second_deriv=f"{second_deriv}"))
            
            # Классификация
            if second_deriv > 0:
                ext_type = types.get("minimum", {}).get(self.language, "minimum")
            else:
                ext_type = types.get("maximum", {}).get(self.language, "maximum")
            
            step4 = templates.get("classify_point", {}).get(self.language, "")
            self.solution_steps.append(step4.format(
                step=4, x=f"{critical_x:.4f}", value=second_deriv, type=ext_type
            ))
            
            critical_y = self._eval_poly(self.coefficients, critical_x)
            self.final_answer = f"x = {critical_x:.4f}, f(x) = {critical_y:.4f} ({ext_type})"
        else:
            # Упрощённое решение для более высоких степеней
            self.final_answer = "Требуется численное решение"
    
    def _solve_max_min_interval(self, templates, types):
        """Max/min на отрезке."""
        a, b = self.interval
        
        # Находим производную и критические точки
        deriv = self._derivative(self.coefficients)
        
        # Для квадратного многочлена
        if len(self.coefficients) == 3:
            coef_a, coef_b, coef_c = self.coefficients
            critical_x = -coef_b / (2 * coef_a)
            
            # Собираем точки для проверки
            points = [a, b]
            if a < critical_x < b:
                points.append(critical_x)
            
            # Вычисляем значения
            values = [(x, self._eval_poly(self.coefficients, x)) for x in points]
            
            max_point = max(values, key=lambda p: p[1])
            min_point = min(values, key=lambda p: p[1])
            
            step = templates.get("check_endpoints", {}).get(self.language, "")
            self.solution_steps.append(step.format(
                step=1, a=a, b=b, 
                fa=f"{self._eval_poly(self.coefficients, a):.4f}",
                fb=f"{self._eval_poly(self.coefficients, b):.4f}"
            ))
            
            self.final_answer = (
                f"max: f({max_point[0]:.4f}) = {max_point[1]:.4f}, "
                f"min: f({min_point[0]:.4f}) = {min_point[1]:.4f}"
            )
        else:
            self.final_answer = "Требуется численное решение"
    
    def _solve_linear_programming(self, templates):
        """Линейное программирование (2D симплекс)."""
        if self.lp_vars != 2:
            self.final_answer = "Требуется симплекс-метод"
            return
        
        # Находим вершины допустимой области
        vertices = self._find_feasible_vertices()
        
        step1 = templates.get("lp_vertices", {}).get(self.language, "")
        vertices_str = ", ".join([f"({v[0]:.2f}, {v[1]:.2f})" for v in vertices])
        self.solution_steps.append(step1.format(step=1, vertices=vertices_str))
        
        # Вычисляем значения целевой функции в вершинах
        objective_values = []
        for v in vertices:
            val = sum(c * x for c, x in zip(self.lp_objective, v))
            objective_values.append((v, val))
        
        step2 = templates.get("evaluate_objective", {}).get(self.language, "")
        values_str = ", ".join([f"f{v} = {val:.2f}" for v, val in objective_values])
        self.solution_steps.append(step2.format(step=2, values=values_str))
        
        # Находим максимум
        best = max(objective_values, key=lambda x: x[1])
        self.final_answer = f"max = {best[1]:.2f} at ({best[0][0]:.2f}, {best[0][1]:.2f})"
    
    def _find_feasible_vertices(self) -> List[Tuple[float, float]]:
        """Находит вершины допустимой области для 2D ЛП."""
        vertices = [(0, 0)]
        
        # Точки пересечения с осями
        for coeffs, rhs in self.lp_constraints:
            if coeffs[0] != 0:
                vertices.append((rhs / coeffs[0], 0))
            if coeffs[1] != 0:
                vertices.append((0, rhs / coeffs[1]))
        
        # Точки пересечения ограничений
        for i, (c1, r1) in enumerate(self.lp_constraints):
            for j, (c2, r2) in enumerate(self.lp_constraints[i+1:], i+1):
                # Решаем систему: c1[0]*x + c1[1]*y = r1, c2[0]*x + c2[1]*y = r2
                det = c1[0] * c2[1] - c1[1] * c2[0]
                if abs(det) > 0.001:
                    x = (r1 * c2[1] - r2 * c1[1]) / det
                    y = (c1[0] * r2 - c2[0] * r1) / det
                    if x >= -0.001 and y >= -0.001:
                        vertices.append((max(0, x), max(0, y)))
        
        # Фильтруем допустимые вершины
        feasible = []
        for v in vertices:
            is_feasible = True
            for coeffs, rhs in self.lp_constraints:
                if sum(c * x for c, x in zip(coeffs, v)) > rhs + 0.001:
                    is_feasible = False
                    break
            if is_feasible and v[0] >= -0.001 and v[1] >= -0.001:
                feasible.append(v)
        
        return feasible if feasible else [(0, 0)]
    
    def get_task_type(self) -> str:
        return "optimization"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        """Генерирует случайную задачу на оптимизацию."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format,
            reasoning_mode=reasoning_mode
        )
