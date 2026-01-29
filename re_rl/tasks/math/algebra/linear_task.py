# re_rl/tasks/linear_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, Optional, ClassVar

class LinearTask(BaseMathTask):
    """
    Решает линейное уравнение вида a*x + b = c.
    
    Параметры сложности:
      - difficulty 1-2: коэффициенты 1-5, целые решения
      - difficulty 3-4: коэффициенты 1-10
      - difficulty 5-6: коэффициенты 1-20
      - difficulty 7-8: коэффициенты 1-50
      - difficulty 9-10: коэффициенты до 100, дробные решения
      
    detail_level задаёт степень детализации решения.
    """
    
    # Пресеты сложности: определяют диапазоны коэффициентов
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 5, "ensure_integer": True},
        2: {"max_coef": 5, "ensure_integer": True},
        3: {"max_coef": 10, "ensure_integer": True},
        4: {"max_coef": 10, "ensure_integer": True},
        5: {"max_coef": 20, "ensure_integer": True},
        6: {"max_coef": 20, "ensure_integer": True},
        7: {"max_coef": 50, "ensure_integer": True},
        8: {"max_coef": 50, "ensure_integer": False},
        9: {"max_coef": 100, "ensure_integer": False},
        10: {"max_coef": 100, "ensure_integer": False},
    }
    
    def __init__(
        self, 
        a=None, 
        b=None, 
        c=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        max_coef: int = 10,
        ensure_integer: bool = True
    ):
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", max_coef)
            ensure_integer = preset.get("ensure_integer", ensure_integer)
        
        # Генерируем коэффициенты, если не заданы
        if a is None or b is None or c is None:
            a, b, c = self._generate_coefficients(max_coef, ensure_integer)
        
        self.a = a
        self.b = b
        self.c = c
        self.difficulty = difficulty
        self.detail_level = detail_level
        
        # Формируем уравнение
        equation = f"{a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}"
        description = PROMPT_TEMPLATES["linear"]["problem"][language].format(equation=equation)
        super().__init__(description, language, detail_level)
    
    @staticmethod
    def _generate_coefficients(max_coef: int, ensure_integer: bool) -> tuple:
        """Генерирует коэффициенты a, b, c для уравнения a*x + b = c."""
        # a не должен быть нулём
        a = random.randint(1, max_coef)
        if random.random() < 0.5:
            a = -a
        
        if ensure_integer:
            # Генерируем x и вычисляем c = a*x + b
            x = random.randint(-max_coef, max_coef)
            b = random.randint(-max_coef, max_coef)
            c = a * x + b
        else:
            b = random.randint(-max_coef, max_coef)
            c = random.randint(-max_coef, max_coef)
        
        return a, b, c

    # Мы просто проксируем к базовому методу, чтобы не дублировать логику
    def add_solution_step(self, step, explanation, validation):  # type: ignore[override]
        super().add_solution_step(step, explanation, validation)

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
            self.solution_steps.clear()
            self.explanation_steps.clear()
            self.validation_steps.clear()
            
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
            "explanations": self.explanation_steps,
            "validations": self.validation_steps,
            "final_answer": self.final_answer,
        })
        
        if detail_level is not None:
            self.detail_level = old_detail_level
            
        return result
