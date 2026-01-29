# re_rl/tasks/linear_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
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
        ensure_integer: bool = True,
        output_format: OutputFormat = "text"
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
        self._output_format = output_format
        
        # Формируем уравнение в нужном формате
        equation = self._format_equation(a, b, c, output_format)
        
        # Всегда используем шаблоны из PROMPT_TEMPLATES
        description = PROMPT_TEMPLATES["linear"]["problem"][language].format(equation=equation)
        
        super().__init__(description, language, detail_level, output_format)
    
    @staticmethod
    def _format_equation(a: int, b: int, c: int, output_format: OutputFormat = "text") -> str:
        """Форматирует уравнение ax + b = c."""
        if output_format == "latex":
            # LaTeX формат
            if a == 1:
                ax = "x"
            elif a == -1:
                ax = "-x"
            else:
                ax = f"{a}x"
            
            if b > 0:
                eq = f"{ax} + {b} = {c}"
            elif b < 0:
                eq = f"{ax} - {abs(b)} = {c}"
            else:
                eq = f"{ax} = {c}"
            return f"${eq}$"
        else:
            # Text формат
            return f"{a}x {'+' if b >= 0 else '-'} {abs(b)} = {c}"
    
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
        solution = sp.solve(eq, x)[0]
        right_side = self.c - self.b
        
        is_latex = self._output_format == "latex"
        step_tmpl = PROMPT_TEMPLATES["default"]["step"][self.language]
        equation_label = PROMPT_TEMPLATES.get("linear", {}).get("equation_label", {"ru": "Уравнение", "en": "Equation"}).get(self.language, "Equation")
        move_label = {"ru": "Переносим", "en": "Move"}.get(self.language, "Move")
        
        # Форматирование в зависимости от формата
        eq_str = self._format_equation(self.a, self.b, self.c, self._output_format)
        
        # Шаг 1: Запись уравнения
        if self.detail_level >= 1:
            text = f"{equation_label}: {eq_str}"
            self.solution_steps.append(step_tmpl.format(n=1, text=text))
        
        # Шаг 2: Переносим b в правую часть
        if self.detail_level >= 2:
            if is_latex:
                text = f"{move_label} {self.b}: ${self.a}x = {self.c} - ({self.b}) = {right_side}$"
            else:
                text = f"{self.a}x = {self.c} - {self.b} = {right_side}"
            self.solution_steps.append(step_tmpl.format(n=2, text=text))
        
        # Шаг 3: Делим на коэффициент
        if self.detail_level >= 3:
            if is_latex:
                sol_latex = sp.latex(solution)
                text = f"$x = \\frac{{{right_side}}}{{{self.a}}} = {sol_latex}$"
            else:
                text = f"x = {right_side} / {self.a} = {solution}"
            self.solution_steps.append(step_tmpl.format(n=3, text=text))
        
        # Финальный ответ
        if is_latex:
            self.final_answer = f"$x = {sp.latex(solution)}$"
        else:
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
