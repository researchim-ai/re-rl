# re_rl/tasks/logarithmic_task.py

import random
import math
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, Optional, ClassVar


class LogarithmicTask(BaseMathTask):
    """Класс для генерации и решения логарифмических уравнений вида a*log(b*x) + c = d"""
    
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
        language="ru", 
        detail_level=3,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", 10)
            if a is None:
                a = random.choice([i for i in range(-max_coef, max_coef+1) if i != 0])
            if b is None:
                b = random.randint(1, max_coef)  # b > 0 для области определения
            if c is None:
                c = random.randint(-max_coef, max_coef)
            if d is None:
                d = random.randint(-max_coef, max_coef)
        
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self._output_format = output_format
        
        # Формируем описание
        equation = self._format_equation(a, b, c, d, output_format)
        
        # Всегда используем шаблоны из PROMPT_TEMPLATES
        description = PROMPT_TEMPLATES["logarithmic"]["problem"][language].format(equation=equation)
        
        super().__init__(description, language, detail_level, output_format)
    
    @staticmethod
    def _format_equation(a, b, c, d, output_format: OutputFormat = "text") -> str:
        """Форматирует уравнение."""
        if output_format == "latex":
            x = sp.Symbol('x')
            expr = a * sp.log(b * x) + c
            return f"${sp.latex(expr)} = {d}$"
        else:
            return f"{a}*log({b}*x) + {c} = {d}"
        
    def solve(self):
        is_latex = self._output_format == "latex"
        step_tmpl = PROMPT_TEMPLATES["default"]["step"][self.language]
        
        # Шаг 1: Переносим c
        right_side = self.d - self.c
        if is_latex:
            text = f"${self.a} \\ln({self.b}x) = {self.d} - {self.c} = {right_side}$"
        else:
            text = f"{self.a}*log({self.b}*x) = {self.d} - {self.c} = {right_side}"
        self.solution_steps.append(step_tmpl.format(n=1, text=text))
        
        # Шаг 2: Делим на a
        log_value = right_side / self.a
        if is_latex:
            text = f"$\\ln({self.b}x) = \\frac{{{right_side}}}{{{self.a}}} = {log_value:.4f}$"
        else:
            text = f"log({self.b}*x) = {right_side}/{self.a} = {log_value:.4f}"
        self.solution_steps.append(step_tmpl.format(n=2, text=text))
        
        # Шаг 3: Применяем exp
        exp_value = math.exp(log_value)
        if is_latex:
            text = f"${self.b}x = e^{{{log_value:.4f}}} = {exp_value:.4f}$"
        else:
            text = f"{self.b}*x = e^{log_value:.4f} = {exp_value:.4f}"
        self.solution_steps.append(step_tmpl.format(n=3, text=text))
        
        # Шаг 4: Решение
        x = exp_value / self.b
        if is_latex:
            text = f"$x = \\frac{{{exp_value:.4f}}}{{{self.b}}} = {x:.4f}$"
            self.final_answer = f"$x = {x:.4f}$"
        else:
            text = f"x = {exp_value:.4f}/{self.b} = {x:.4f}"
            self.final_answer = f"{x:.4f}"
        self.solution_steps.append(step_tmpl.format(n=4, text=text))

    def get_task_type(self):
        return "logarithmic"
