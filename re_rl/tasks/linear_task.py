# re_rl/tasks/linear_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class LinearTask(BaseMathTask):
    """
    Класс для решения линейного уравнения вида a*x + b = c.
    """
    def __init__(self, a, b, c, language: str = "ru"):
        self.a = a
        self.b = b
        self.c = c
        equation = f"{a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}"
        description = PROMPT_TEMPLATES["linear"]["problem"][language].format(equation=equation)
        super().__init__(description, language)

    def solve(self):
        x = sp.symbols('x')
        equation = sp.Eq(self.a*x + self.b, self.c)
        eq_pretty = sp.pretty(equation)
        step1 = PROMPT_TEMPLATES["linear"]["step1"][self.language].format(equation_pretty=eq_pretty)
        right_side = self.c - self.b
        step2 = PROMPT_TEMPLATES["linear"]["step2"][self.language].format(a=self.a, b=self.b, c=self.c, right_side=right_side)
        solution = sp.solve(equation, x)
        step3 = PROMPT_TEMPLATES["linear"]["step3"][self.language].format(a=self.a, right_side=right_side, solution=solution[0])
        self.solution_steps.extend([step1, step2, step3])
        self.final_answer = str(solution[0])

    def get_task_type(self):
        return "linear"
