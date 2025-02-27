# re_rl/tasks/cubic_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class CubicTask(BaseMathTask):
    """
    Класс для решения кубического уравнения: a*x³ + b*x² + c*x + d = 0.
    """
    def __init__(self, a, b, c, d, language: str = "ru"):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        x = sp.symbols('x')
        eq_expr = self.a*x**3 + self.b*x**2 + self.c*x + self.d
        equation_pretty = sp.pretty(eq_expr)
        description = PROMPT_TEMPLATES["cubic"]["problem"][language].format(equation_pretty=equation_pretty)
        super().__init__(description, language)

    def solve(self):
        x = sp.symbols('x')
        equation = sp.Eq(self.a*x**3 + self.b*x**2 + self.c*x + self.d, 0)
        eq_pretty = sp.pretty(equation)
        step1 = PROMPT_TEMPLATES["cubic"]["step1"][self.language].format(equation_pretty=eq_pretty)
        roots = sp.solve(equation, x)
        step2 = PROMPT_TEMPLATES["cubic"]["step2"][self.language].format(roots=roots)
        self.solution_steps.extend([step1, step2])
        self.final_answer = str(roots)

    def get_task_type(self):
        return "cubic"
