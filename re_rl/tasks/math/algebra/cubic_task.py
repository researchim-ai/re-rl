# re_rl/tasks/cubic_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, ClassVar


class CubicTask(BaseMathTask):
    """
    Решает кубическое уравнение: a*x³ + b*x² + c*x + d = 0.
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 3},
        3: {"max_coef": 5},
        5: {"max_coef": 10},
        7: {"max_coef": 15},
        10: {"max_coef": 20},
    }
    
    def __init__(
        self, 
        a=None, 
        b=None, 
        c=None, 
        d=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", 10)
            if a is None:
                a = random.randint(1, max_coef)
                if random.random() < 0.3:
                    a = -a
            if b is None:
                b = random.randint(-max_coef, max_coef)
            if c is None:
                c = random.randint(-max_coef, max_coef)
            if d is None:
                d = random.randint(-max_coef, max_coef)
        
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self._output_format = output_format
        
        # Формируем уравнение
        equation = self._format_equation(a, b, c, d, output_format)
        
        # Всегда используем шаблоны из PROMPT_TEMPLATES
        description = PROMPT_TEMPLATES["cubic"]["problem"][language].format(equation_pretty=equation)
        
        super().__init__(description, language, detail_level, output_format)
    
    @staticmethod
    def _format_equation(a, b, c, d, output_format: OutputFormat = "text") -> str:
        """Форматирует кубическое уравнение."""
        x = sp.Symbol('x')
        expr = a*x**3 + b*x**2 + c*x + d
        
        if output_format == "latex":
            return f"${sp.latex(expr)} = 0$"
        else:
            return sp.pretty(expr)

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*x**3 + self.b*x**2 + self.c*x + self.d, 0)
        roots = sp.solve(eq, x)
        
        is_latex = self._output_format == "latex"
        step_tmpl = PROMPT_TEMPLATES["default"]["step"][self.language]
        eq_label = PROMPT_TEMPLATES["default"]["equation"][self.language]
        roots_label = PROMPT_TEMPLATES["default"]["roots"][self.language]
        
        # Шаг 1
        eq_str = self._format_equation(self.a, self.b, self.c, self.d, self._output_format)
        text = f"{eq_label}: {eq_str}"
        self.solution_steps.append(step_tmpl.format(n=1, text=text))
        
        # Шаг 2: Корни
        if is_latex:
            roots_latex = ", ".join(sp.latex(r) for r in roots)
            text = f"{roots_label}: ${roots_latex}$"
            self.final_answer = f"${roots_latex}$"
        else:
            text = f"{roots_label}: {roots}"
            self.final_answer = str(roots)
        self.solution_steps.append(step_tmpl.format(n=2, text=text))

    def get_task_type(self):
        return "cubic"
