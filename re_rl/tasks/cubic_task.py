# re_rl/tasks/cubic_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class CubicTask(BaseMathTask):
    """
    Решает кубическое уравнение: a*x³ + b*x² + c*x + d = 0.
    """
    def __init__(self, a, b, c, d, language: str = "ru", detail_level: int = 3):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        x = sp.symbols('x')
        eq_expr = self.a*x**3 + self.b*x**2 + self.c*x + self.d
        equation_pretty = sp.pretty(eq_expr)
        description = PROMPT_TEMPLATES["cubic"]["problem"][language].format(equation_pretty=equation_pretty)
        super().__init__(description, language, detail_level)

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*x**3 + self.b*x**2 + self.c*x + self.d, 0)
        eq_pretty = sp.pretty(eq)
        steps = []
        steps.append(PROMPT_TEMPLATES["cubic"]["step1"][self.language].format(equation_pretty=eq_pretty))
        roots = sp.solve(eq, x)
        steps.append(PROMPT_TEMPLATES["cubic"]["step2"][self.language].format(roots=roots))
        self.solution_steps.extend(steps)
        self.final_answer = str(roots)

    def get_task_type(self):
        return "cubic"
