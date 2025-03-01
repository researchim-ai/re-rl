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
        steps = []
        # Шаг 1: Запись уравнения
        steps.append(PROMPT_TEMPLATES["linear"]["step1"][self.language].format(equation_pretty=eq_pretty))
        
        # Если detail_level >= 2, добавляем шаг вычисления правой части
        if self.detail_level >= 2:
            right_side = self.c - self.b
            steps.append(PROMPT_TEMPLATES["linear"]["step2"][self.language].format(c=self.c, b=self.b, right_side=right_side))
        else:
            # Для detail_level 1 используем 0 как правую часть для дальнейшего решения (но этот шаг не выводится)
            right_side = self.c - self.b
        
        solution = sp.solve(eq, x)
        
        # Если detail_level >= 3, добавляем шаг деления
        if self.detail_level >= 3:
            # Если detail_level > 3, добавляем дополнительные шаги
            if self.detail_level > 3:
                extra = self.detail_level - 3  # число дополнительных шагов
                # Разобьём right_side на extra равных частей
                part = right_side / extra
                parts = [round(part, 2)] * extra
                sum_parts = round(sum(parts), 2)
                # Если из-за округления сумма не совпадает, корректируем первое слагаемое
                diff = round(right_side - sum_parts, 2)
                if diff != 0 and extra > 0:
                    parts[0] += diff
                steps.append(PROMPT_TEMPLATES["linear"]["linear_extra_partition"][self.language].format(c=self.c, b=self.b, n=extra, parts=parts))
                steps.append(PROMPT_TEMPLATES["linear"]["linear_extra_sum"][self.language].format(sum_value=round(sum(parts), 2)))
            steps.append(PROMPT_TEMPLATES["linear"]["step3"][self.language].format(a=self.a, right_side=right_side, solution=solution[0]))
        self.solution_steps = steps
        self.final_answer = str(solution[0])

    def get_task_type(self):
        return "linear"
