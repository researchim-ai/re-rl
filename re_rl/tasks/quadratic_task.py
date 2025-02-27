# re_rl/tasks/quadratic_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class QuadraticTask(BaseMathTask):
    """
    Класс для решения квадратного уравнения: a*x² + b*x + c = 0.
    """
    def __init__(self, a, b, c, language: str = "ru"):
        self.a = a
        self.b = b
        self.c = c
        x = sp.symbols('x')
        eq_expr = self.a*x**2 + self.b*x + self.c
        equation_pretty = sp.pretty(eq_expr)
        description = PROMPT_TEMPLATES["quadratic"]["problem"][language].format(equation_pretty=equation_pretty)
        super().__init__(description, language)

    def solve(self):
        x = sp.symbols('x')
        equation = sp.Eq(self.a*x**2 + self.b*x + self.c, 0)
        eq_pretty = sp.pretty(equation)
        step1 = PROMPT_TEMPLATES["quadratic"]["step1"][self.language].format(equation_pretty=eq_pretty)
        discriminant = self.b**2 - 4*self.a*self.c
        step2 = PROMPT_TEMPLATES["quadratic"]["step2"][self.language].format(a=self.a, b=self.b, c=self.c, discriminant=discriminant)
        roots = sp.solve(equation, x)
        step3 = PROMPT_TEMPLATES["quadratic"]["step3"][self.language].format(roots=roots)
        self.solution_steps.extend([step1, step2, step3])
        self.final_answer = str(roots)

    def get_task_type(self):
        return "quadratic"
