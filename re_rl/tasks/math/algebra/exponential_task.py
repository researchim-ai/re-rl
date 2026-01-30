# re_rl/tasks/exponential_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any, ClassVar


class ExponentialTask(BaseMathTask):
    """
    Решает экспоненциальное уравнение: a*exp(b*x) + c = d.
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
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", 10)
            if a is None:
                a = random.choice([i for i in range(-max_coef, max_coef+1) if i != 0])
            if b is None:
                b = random.choice([i for i in range(-max_coef, max_coef+1) if i != 0])
            if c is None:
                c = random.randint(-max_coef, max_coef)
            if d is None:
                d = random.randint(-max_coef, max_coef)
        
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Формируем описание
        equation = self._format_equation(a, b, c, d, output_format)
        
        # Всегда используем шаблоны из PROMPT_TEMPLATES
        description = PROMPT_TEMPLATES["exponential"]["problem"][language].format(equation=equation)
        
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    @staticmethod
    def _format_equation(a, b, c, d, output_format: OutputFormat = "text") -> str:
        """Форматирует уравнение."""
        if output_format == "latex":
            x = sp.Symbol('x')
            expr = a * sp.exp(b * x) + c
            return f"${sp.latex(expr)} = {d}$"
        else:
            left = f"{'' if abs(a)==1 else abs(a)}exp({'' if abs(b)==1 else abs(b)}*x)"
            c_term = f" + {c}" if c >= 0 else f" - {abs(c)}"
            return f"{left}{c_term} = {d}"

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*sp.exp(self.b*x) + self.c, self.d)
        
        is_latex = self._output_format == "latex"
        step_tmpl = PROMPT_TEMPLATES["default"]["step"][self.language]
        
        steps = []
        
        # Шаг 1
        eq_str = self._format_equation(self.a, self.b, self.c, self.d, self._output_format)
        equation_text = PROMPT_TEMPLATES["exponential"].get("equation_label", {"ru": "Уравнение", "en": "Equation"}).get(self.language, "Equation")
        text = f"{equation_text}: {eq_str}"
        steps.append(step_tmpl.format(n=1, text=text))
        
        # Шаг 2: Переносим c
        right_side = self.d - self.c
        if is_latex:
            text = f"${self.a} e^{{{self.b}x}} = {self.d} - {self.c} = {right_side}$"
        else:
            text = f"{self.a}*exp({self.b}*x) = {self.d} - {self.c} = {right_side}"
        steps.append(step_tmpl.format(n=2, text=text))
        
        ratio = right_side / self.a
        
        if ratio <= 0:
            error_msg = PROMPT_TEMPLATES["default"]["no_solution"].get(self.language, "No solution")
            steps.append(error_msg)
            self.solution_steps.extend(steps)
            self.final_answer = error_msg
            return
        
        # Шаг 3: Решение
        sol_val = sp.log(ratio) / self.b
        if is_latex:
            text = f"$x = \\frac{{\\ln({ratio})}}{{{self.b}}} = {sp.latex(sol_val)}$"
            self.final_answer = f"$x = {sp.latex(sol_val)}$"
        else:
            text = f"x = ln({ratio}) / {self.b} = {sol_val}"
            self.final_answer = str(sol_val)
        steps.append(step_tmpl.format(n=3, text=text))
        
        self.solution_steps.extend(steps)

    def get_task_type(self):
        return "exponential"
