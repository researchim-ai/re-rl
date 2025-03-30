# re_rl/tasks/linear_task.py

import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

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
        equation = f"{a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}"
        description = PROMPT_TEMPLATES["linear"]["problem"][language].format(equation=equation)
        super().__init__(description, language, detail_level)

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a * x + self.b, self.c)
        eq_pretty = sp.pretty(eq)
        
        # Шаг 1: Запись уравнения
        step1 = PROMPT_TEMPLATES["linear"]["step1"][self.language].format(equation_pretty=eq_pretty)
        explanation1 = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step1"]
        validation1 = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step1"]
        self.add_solution_step(step1, explanation1, validation1)
        
        # Шаг 2: Анализ уравнения
        step2_analysis = PROMPT_TEMPLATES["linear"]["step2_analysis"][self.language].format(
            a=self.a, b=self.b, c=self.c
        )
        explanation2_analysis = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step2_analysis"]
        validation2_analysis = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step2_analysis"]
        self.add_solution_step(step2_analysis, explanation2_analysis, validation2_analysis)
        
        # Шаг 3: Выделение слагаемых
        step3_terms = PROMPT_TEMPLATES["linear"]["step3_terms"][self.language].format(
            a=self.a, b=self.b, c=self.c
        )
        explanation3_terms = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step3_terms"]
        validation3_terms = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step3_terms"]
        self.add_solution_step(step3_terms, explanation3_terms, validation3_terms)
        
        # Шаг 4: Перенос слагаемых
        right_side = self.c - self.b
        step4_transfer = PROMPT_TEMPLATES["linear"]["step4_transfer"][self.language].format(
            c=self.c, b=self.b, right_side=right_side
        )
        explanation4_transfer = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step4_transfer"]
        validation4_transfer = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step4_transfer"]
        self.add_solution_step(step4_transfer, explanation4_transfer, validation4_transfer)
        
        # Шаг 5: Проверка коэффициента при x
        step5_coef = PROMPT_TEMPLATES["linear"]["step5_coef"][self.language].format(
            a=self.a
        )
        explanation5_coef = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step5_coef"]
        validation5_coef = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step5_coef"]
        self.add_solution_step(step5_coef, explanation5_coef, validation5_coef)
        
        # Шаг 6: Деление на коэффициент
        solution = sp.solve(eq, x)
        if not solution:
            raise ValueError(f"Уравнение {eq} не имеет решений")
            
        step6_division = PROMPT_TEMPLATES["linear"]["step6_division"][self.language].format(
            a=self.a, right_side=right_side, solution=solution[0]
        )
        explanation6_division = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step6_division"]
        validation6_division = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step6_division"]
        self.add_solution_step(step6_division, explanation6_division, validation6_division)
        
        # Шаг 7: Проверка решения
        step7_check = PROMPT_TEMPLATES["linear"]["step7_check"][self.language].format(
            solution=solution[0], equation=eq_pretty
        )
        explanation7_check = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step7_check"]
        validation7_check = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step7_check"]
        self.add_solution_step(step7_check, explanation7_check, validation7_check)
        
        # Если detail_level > 7, добавляем дополнительные шаги
        if self.detail_level > 7:
            # Шаг 8: Геометрическая интерпретация
            step8_geom = PROMPT_TEMPLATES["linear"]["step8_geom"][self.language].format(
                a=self.a, b=self.b, c=self.c, solution=solution[0]
            )
            explanation8_geom = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step8_geom"]
            validation8_geom = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step8_geom"]
            self.add_solution_step(step8_geom, explanation8_geom, validation8_geom)
            
            # Шаг 9: Альтернативный метод решения
            step9_alt = PROMPT_TEMPLATES["linear"]["step9_alt"][self.language].format(
                a=self.a, b=self.b, c=self.c, solution=solution[0]
            )
            explanation9_alt = PROMPT_TEMPLATES["linear"]["explanation"][self.language]["step9_alt"]
            validation9_alt = PROMPT_TEMPLATES["linear"]["validation"][self.language]["step9_alt"]
            self.add_solution_step(step9_alt, explanation9_alt, validation9_alt)
            
        self.final_answer = str(solution[0])

    def get_task_type(self):
        return "linear"
