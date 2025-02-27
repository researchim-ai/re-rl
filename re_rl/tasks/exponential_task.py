# re_rl/tasks/exponential_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class ExponentialTask(BaseMathTask):
    """
    Класс для решения экспоненциального уравнения: a*exp(b*x) + c = d.
    """
    def __init__(self, a, b, c, d, language: str = "ru"):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        left = f"{'' if abs(a)==1 else abs(a)}exp({'' if abs(b)==1 else abs(b)}*x)"
        c_term = f" + {self.c}" if self.c >= 0 else f" - {abs(self.c)}"
        description = PROMPT_TEMPLATES["exponential"]["problem"][language].format(left=left + c_term, d=self.d)
        super().__init__(description, language)

    def solve(self):
        x = sp.symbols('x')
        equation = sp.Eq(self.a*sp.exp(self.b*x) + self.c, self.d)
        eq_pretty = sp.pretty(equation)
        step1 = PROMPT_TEMPLATES["exponential"]["step1"][self.language].format(equation_pretty=eq_pretty)
        left_side_statement = f"{self.a}*exp({self.b}*x) = {self.d} - {self.c}"
        step2 = PROMPT_TEMPLATES["exponential"]["step2"][self.language].format(c=self.c, left_side_statement=left_side_statement)
        right_side = self.d - self.c
        step3 = PROMPT_TEMPLATES["exponential"]["step3"][self.language].format(a=self.a, b=self.b, right_side=right_side)
        ratio = right_side / self.a
        if ratio <= 0:
            self.solution_steps.extend([step1, step2, step3])
            self.solution_steps.append("Шаг 4: Нет решений, так как аргумент логарифма не положительный.")
            self.final_answer = "Нет решений"
        else:
            sol_val = sp.log(ratio) / self.b
            step4 = PROMPT_TEMPLATES["exponential"]["step4"][self.language].format(ratio=ratio, b=self.b, solution=sol_val)
            self.solution_steps.extend([step1, step2, step3, step4])
            self.final_answer = str(sol_val)

    def get_task_type(self):
        return "exponential"
