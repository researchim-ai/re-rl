# re_rl/tasks/exponential_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any

class ExponentialTask(BaseMathTask):
    """
    Решает экспоненциальное уравнение: a*exp(b*x) + c = d.
    """
    def __init__(self, a, b, c, d, language: str = "ru", detail_level: int = 3):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        left = f"{'' if abs(a)==1 else abs(a)}exp({'' if abs(b)==1 else abs(b)}*x)"
        c_term = f" + {self.c}" if self.c >= 0 else f" - {abs(self.c)}"
        description = PROMPT_TEMPLATES["exponential"]["problem"][language].format(left=left+c_term, d=self.d)
        super().__init__(description, language, detail_level)

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*sp.exp(self.b*x) + self.c, self.d)
        eq_pretty = sp.pretty(eq)
        steps = []
        steps.append(PROMPT_TEMPLATES["exponential"]["step1"][self.language].format(equation_pretty=eq_pretty))
        left_side_statement = f"{self.a}*exp({self.b}*x) = {self.d} - {self.c}"
        steps.append(PROMPT_TEMPLATES["exponential"]["step2"][self.language].format(c=self.c, left_side_statement=left_side_statement))
        right_side = self.d - self.c
        ratio = right_side / self.a
        steps.append(PROMPT_TEMPLATES["exponential"]["step3"][self.language].format(a=self.a, b=self.b, right_side=right_side, ratio=ratio))
        if ratio <= 0:
            error_msg = PROMPT_TEMPLATES["default"]["no_solution"].get(self.language, PROMPT_TEMPLATES["default"]["no_solution"]["en"])
            steps.append(error_msg)
            self.solution_steps.extend(steps)
            self.final_answer = error_msg
        else:
            sol_val = sp.log(ratio) / self.b
            if self.detail_level >= 4:
                substep1 = f"Вычисляем log({ratio})"
                substep2 = f"Делим на {self.b}: получаем {sol_val}"
                steps.extend([substep1, substep2])
            steps.append(PROMPT_TEMPLATES["exponential"]["step4"][self.language].format(ratio=ratio, b=self.b, solution=sol_val))
            self.solution_steps.extend(steps)
            self.final_answer = str(sol_val)

    def get_task_type(self):
        return "exponential"

    def get_result(self, detail_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Возвращает результат решения с заданным уровнем детализации.
        
        Args:
            detail_level: Уровень детализации решения. Если не указан, используется self.detail_level
            
        Returns:
            Dict[str, Any]: Результат решения
        """
        if detail_level is None:
            detail_level = self.detail_level
            
        result = super().get_result()
        
        # Решаем уравнение, если еще не решено
        if not self.solution_steps:
            self.solve()
            
        result["final_answer"] = self.final_answer
        return result
