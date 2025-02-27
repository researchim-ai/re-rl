# re_rl/tasks/calculus_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class CalculusTask(BaseMathTask):
    """
    Класс для задач по анализу: дифференцирование и интегрирование полиномиальных функций.
    task_type может быть "differentiation" или "integration".
    """
    def __init__(self, task_type="differentiation", degree=2, language: str = "ru"):
        self.task_type = task_type.lower()
        self.degree = degree
        self.function = None
        super().__init__("", language)

    def generate_function(self):
        x = sp.symbols('x')
        coeffs = [random.randint(-5, 5) for _ in range(self.degree+1)]
        while coeffs[-1] == 0:
            coeffs[-1] = random.randint(-5, 5)
        poly = sum(coeffs[i]*x**i for i in range(self.degree+1))
        self.function = sp.simplify(poly)

    def _create_problem_description(self):
        self.generate_function()
        function_pretty = sp.pretty(self.function)
        task_type_text = "производную" if self.task_type=="differentiation" else "неопределённый интеграл"
        return PROMPT_TEMPLATES["calculus"]["problem"][self.language].format(task_type=task_type_text, function_pretty=function_pretty)

    def solve(self):
        x = sp.symbols('x')
        self.description = self._create_problem_description()
        function_pretty = sp.pretty(self.function)
        step1 = PROMPT_TEMPLATES["calculus"]["step1"][self.language].format(function_pretty=function_pretty)
        if self.task_type=="differentiation":
            result_expr = sp.diff(self.function, x)
            step2 = PROMPT_TEMPLATES["calculus"]["step2"][self.language].format(task_type="производную", result=sp.pretty(result_expr))
            self.final_answer = sp.pretty(result_expr)
        elif self.task_type=="integration":
            result_expr = sp.integrate(self.function, x)
            step2 = PROMPT_TEMPLATES["calculus"]["step2"][self.language].format(task_type="неопределённый интеграл", result=sp.pretty(result_expr)+" + C")
            self.final_answer = sp.pretty(result_expr)+" + C"
        else:
            step2 = "Неизвестный тип задачи."
            self.final_answer = "Нет решения"
        self.solution_steps.extend([step1, step2])

    def get_task_type(self):
        return "calculus"

    @classmethod
    def generate_random_task(cls, task_type="differentiation", degree=None, language: str = "ru"):
        if degree is None:
            degree = random.randint(1,3)
        task = cls(task_type=task_type, degree=degree, language=language)
        task.solve()
        return task
