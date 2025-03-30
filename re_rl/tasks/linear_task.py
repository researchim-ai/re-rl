# re_rl/tasks/linear_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, Optional

class LinearTask(BaseMathTask):
    """
    Решает линейное уравнение вида a*x + b = c.
    Параметр detail_level задаёт степень детализации:
      - 1: только шаг 1 (запись уравнения)
      - 2: шаги 1 и 2 (запись уравнения и вычисление правой части)
      - 3: шаги 1, 2 и 3 (базовый алгоритм)
      - >3: дополнительные шаги для разбиения разности (c - b)
    """
    def __init__(self, a, b, c, language: str = "ru", detail_level: int = 3):
        self.a = a
        self.b = b
        self.c = c
        self.detail_level = detail_level
        self.solution_steps = []
        self.explanations = []
        self.validations = []
        equation = f"{a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}"
        description = PROMPT_TEMPLATES["linear"]["problem"][language].format(equation=equation)
        super().__init__(description, language, detail_level)

    def add_solution_step(self, step, explanation, validation):
        self.solution_steps.append(step)
        self.explanations.append(explanation)
        self.validations.append(validation)

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a * x + self.b, self.c)
        eq_pretty = sp.pretty(eq)
        solution = sp.solve(eq, x)[0]
        right_side = self.c - self.b
        
        # Шаг 1: Запись уравнения
        if self.detail_level >= 1:
            step1 = PROMPT_TEMPLATES["linear"]["step1"][self.language].format(equation_pretty=eq_pretty)
            explanation1 = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step1"]
            validation1 = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step1"]
            self.add_solution_step(step1, explanation1, validation1)
        
        # Шаг 2: Анализ уравнения
        if self.detail_level >= 2:
            step2_analysis = PROMPT_TEMPLATES["linear"]["step2_analysis"][self.language].format(
                a=self.a, b=self.b, c=self.c
            )
            explanation2_analysis = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step2_analysis"]
            validation2_analysis = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step2_analysis"]
            self.add_solution_step(step2_analysis, explanation2_analysis, validation2_analysis)
        
        # Шаг 3: Перенос свободного члена
        if self.detail_level >= 3:
            step3_transfer = "Шаг 3: Переносим свободный член в правую часть:\n{c} - {b} = {right_side}".format(
                c=self.c, b=self.b, right_side=right_side
            )
            explanation3_transfer = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step4_transfer"]
            validation3_transfer = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step4_transfer"]
            self.add_solution_step(step3_transfer, explanation3_transfer, validation3_transfer)
        
        # Шаг 4: Делим на коэффициент
        if self.detail_level >= 4:
            step4_division = PROMPT_TEMPLATES["linear"]["step6_division"][self.language].format(
                a=self.a, right_side=right_side, solution=solution
            )
            explanation4_division = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step6_division"]
            validation4_division = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step6_division"]
            self.add_solution_step(step4_division, explanation4_division, validation4_division)
        
        # Шаг 5: Решаем уравнение
        if self.detail_level >= 5:
            step5_solve = "Шаг 5: Решаем уравнение:\nx = {solution}".format(solution=solution)
            explanation5_solve = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step7_check"]
            validation5_solve = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step7_check"]
            self.add_solution_step(step5_solve, explanation5_solve, validation5_solve)
        
        self.final_answer = str(solution)

    def get_task_type(self):
        return "linear"

    def get_result(self, detail_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Возвращает результат решения с заданным уровнем детализации.
        
        Args:
            detail_level: Уровень детализации решения (1-7). Если не указан, используется self.detail_level
            
        Returns:
            Dict[str, Any]: Результат решения
        """
        if detail_level is not None:
            old_detail_level = self.detail_level
            self.detail_level = detail_level
            self.solution_steps = []
            self.explanations = []
            self.validations = []
            
        # Получаем базовый результат от родительского класса, но без вызова solve()
        result = {
            "problem": self.description,
            "language": self.language,
            "detail_level": self.detail_level,
            "prompt": PROMPT_TEMPLATES["default"]["prompt"][self.language].format(problem=self.description)
        }
        
        # Добавляем шаги решения
        self.solve()
        
        # Обновляем результат с новыми шагами
        result.update({
            "solution_steps": self.solution_steps,
            "explanations": self.explanations,
            "validations": self.validations,
            "final_answer": self.final_answer
        })
        
        if detail_level is not None:
            self.detail_level = old_detail_level
            
        return result
