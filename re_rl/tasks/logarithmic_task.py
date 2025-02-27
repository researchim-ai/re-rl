# re_rl/tasks/logarithmic_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class LogarithmicTask(BaseMathTask):
    """
    Класс для решения логарифмического уравнения: a*log(b*x) + c = d.
    """
    def __init__(self, a, b, c, d, language: str = "ru"):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        left = f"{'' if abs(a)==1 else abs(a)}log({b}*x)"
        left = (f"{'' if a > 0 else '-'}" + left +
                (f" + {self.c}" if self.c >= 0 else f" - {abs(self.c)}"))
        description = PROMPT_TEMPLATES["logarithmic"]["problem"][language].format(left=left, d=self.d)
        super().__init__(description, language)

    def solve(self):
        x = sp.symbols('x', positive=True)
        equation = sp.Eq(self.a*sp.log(self.b*x) + self.c, self.d)
        eq_pretty = sp.pretty(equation)
        step1 = PROMPT_TEMPLATES["logarithmic"]["step1"][self.language].format(equation_pretty=eq_pretty)
        left_side_statement = f"{self.a}*log({self.b}*x) = {self.d} - {self.c}"
        step2 = PROMPT_TEMPLATES["logarithmic"]["step2"][self.language].format(c=self.c, left_side_statement=left_side_statement)
        step3 = PROMPT_TEMPLATES["logarithmic"]["step3"][self.language].format(a=self.a, b=self.b, d=self.d, c=self.c)
        sol_val = sp.exp((self.d - self.c)/self.a) / self.b
        step4 = PROMPT_TEMPLATES["logarithmic"]["step4"][self.language].format(a=self.a, d=self.d, c=self.c, b=self.b, solution=sol_val)
        self.solution_steps.extend([step1, step2, step3, step4])
        self.final_answer = str(sol_val)

    def get_task_type(self):
        return "logarithmic"
