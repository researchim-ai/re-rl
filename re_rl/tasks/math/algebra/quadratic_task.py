# re_rl/tasks/quadratic_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.formatting import MathFormatter
from typing import Dict, Any, ClassVar

class QuadraticTask(BaseMathTask):
    """
    Решает квадратное уравнение: a*x² + b*x + c = 0.
    
    Параметры сложности:
      - difficulty 1-2: коэффициенты 1-3, целые корни
      - difficulty 3-4: коэффициенты 1-5, целые корни
      - difficulty 5-6: коэффициенты 1-10
      - difficulty 7-8: коэффициенты 1-20
      - difficulty 9-10: коэффициенты до 50, иррациональные корни
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 3, "ensure_integer_roots": True},
        2: {"max_coef": 3, "ensure_integer_roots": True},
        3: {"max_coef": 5, "ensure_integer_roots": True},
        4: {"max_coef": 5, "ensure_integer_roots": True},
        5: {"max_coef": 10, "ensure_integer_roots": True},
        6: {"max_coef": 10, "ensure_integer_roots": False},
        7: {"max_coef": 20, "ensure_integer_roots": False},
        8: {"max_coef": 20, "ensure_integer_roots": False},
        9: {"max_coef": 50, "ensure_integer_roots": False},
        10: {"max_coef": 50, "ensure_integer_roots": False},
    }
    
    def __init__(
        self, 
        a=None, 
        b=None, 
        c=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        max_coef: int = 5,
        ensure_integer_roots: bool = True,
        output_format: OutputFormat = "text"
    ):
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", max_coef)
            ensure_integer_roots = preset.get("ensure_integer_roots", ensure_integer_roots)
        
        # Генерируем коэффициенты, если не заданы
        if a is None or b is None or c is None:
            a, b, c = self._generate_coefficients(max_coef, ensure_integer_roots)
        
        self.a = a
        self.b = b
        self.c = c
        self.difficulty = difficulty
        self._output_format = output_format
        
        # Формируем уравнение в нужном формате (всегда с "= 0")
        equation_str = self._format_equation(a, b, c, output_format, include_equals_zero=True)
        
        # Всегда используем шаблоны из PROMPT_TEMPLATES
        description = PROMPT_TEMPLATES["quadratic"]["problem"][language].format(equation_pretty=equation_str)
        
        super().__init__(description, language, detail_level, output_format)
    
    @staticmethod
    def _format_equation(a: int, b: int, c: int, output_format: OutputFormat = "text", include_equals_zero: bool = False) -> str:
        """
        Форматирует уравнение ax² + bx + c.
        
        Args:
            a, b, c: Коэффициенты
            output_format: "text" или "latex"
            include_equals_zero: Включать "= 0" в формулу
        """
        if output_format == "latex":
            # Используем sympy для LaTeX
            x = sp.Symbol('x')
            expr = a*x**2 + b*x + c
            latex_str = sp.latex(expr)
            if include_equals_zero:
                return f"${latex_str} = 0$"
            return f"${latex_str}$"
        
        # Text формат
        parts = []
        
        # Член с x²
        if a == 1:
            parts.append("x²")
        elif a == -1:
            parts.append("-x²")
        else:
            parts.append(f"{a}x²")
        
        # Член с x
        if b > 0:
            if b == 1:
                parts.append(" + x")
            else:
                parts.append(f" + {b}x")
        elif b < 0:
            if b == -1:
                parts.append(" - x")
            else:
                parts.append(f" - {abs(b)}x")
        
        # Свободный член
        if c > 0:
            parts.append(f" + {c}")
        elif c < 0:
            parts.append(f" - {abs(c)}")
        
        result = "".join(parts)
        if include_equals_zero:
            result += " = 0"
        return result
    
    @staticmethod
    def _generate_coefficients(max_coef: int, ensure_integer_roots: bool) -> tuple:
        """Генерирует коэффициенты для квадратного уравнения."""
        if ensure_integer_roots:
            # Генерируем целые корни x1, x2 и вычисляем коэффициенты
            # (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
            x1 = random.randint(-max_coef, max_coef)
            x2 = random.randint(-max_coef, max_coef)
            a = 1
            b = -(x1 + x2)
            c = x1 * x2
        else:
            a = random.randint(1, max_coef)
            if random.random() < 0.3:
                a = -a
            b = random.randint(-max_coef, max_coef)
            c = random.randint(-max_coef, max_coef)
        
        return a, b, c

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*x**2 + self.b*x + self.c, 0)
        equation_str = self._format_equation(self.a, self.b, self.c, self._output_format, include_equals_zero=True)
        
        steps = []
        
        # Шаг 1: Записываем уравнение
        if self._output_format == "latex":
            if self.language == "ru":
                steps.append(f"Шаг 1: Записываем уравнение в стандартной форме: {equation_str}")
            else:
                steps.append(f"Step 1: Write the equation in standard form: {equation_str}")
        else:
            steps.append(PROMPT_TEMPLATES["quadratic"]["step1"][self.language].format(
                equation_pretty=self._format_equation(self.a, self.b, self.c, self._output_format)
            ))
        
        discriminant = self.b**2 - 4*self.a*self.c
        
        # Шаг 2: Дискриминант
        if self._output_format == "latex":
            disc_formula = f"D = b^2 - 4ac = ({self.b})^2 - 4 \\cdot ({self.a}) \\cdot ({self.c}) = {discriminant}"
            if self.language == "ru":
                steps.append(f"Шаг 2: Вычисляем дискриминант: ${disc_formula}$")
            else:
                steps.append(f"Step 2: Calculate discriminant: ${disc_formula}$")
        else:
            steps.append(PROMPT_TEMPLATES["quadratic"]["step2"][self.language].format(
                a=self.a, b=self.b, c=self.c, discriminant=discriminant
            ))
        
        roots = sp.solve(eq, x)
        
        # Шаг 3: Корни
        if self._output_format == "latex":
            roots_latex = [sp.latex(r) for r in roots]
            if len(roots) == 1:
                roots_display = f"$x = {roots_latex[0]}$"
            else:
                roots_display = f"$x_1 = {roots_latex[0]}, x_2 = {roots_latex[1]}$"
        else:
            roots_str = ", ".join(str(r) for r in roots)
            roots_display = roots_str
            
        if self._output_format == "latex":
            if self.language == "ru":
                steps.append(f"Шаг 3: Находим корни: {roots_display}")
            else:
                steps.append(f"Step 3: Find roots: {roots_display}")
        else:
            steps.append(PROMPT_TEMPLATES["quadratic"]["step3"][self.language].format(roots=roots_display))
        
        self.solution_steps.extend(steps)
        self.final_answer = roots_display

    def get_task_type(self):
        return "quadratic"
