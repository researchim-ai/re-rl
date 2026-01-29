# re_rl/tasks/quadratic_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, ClassVar

class QuadraticTask(BaseMathTask):
    """
    Решает квадратное уравнение: a*x² + b*x + c = 0.
    
    Параметры сложности:
      - difficulty 1-2: коэффициенты 1-3, целые корни
      - difficulty 3-4: коэффициенты 1-5, целые корни
      - difficulty 5-6: коэффициенты 1-10
      - difficulty 7-8: коэффициенты 1-20
      - difficulty 9-10: коэффициенты до 50, иррациональные корни
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coef": 3, "ensure_integer_roots": True},
        2: {"max_coef": 3, "ensure_integer_roots": True},
        3: {"max_coef": 5, "ensure_integer_roots": True},
        4: {"max_coef": 5, "ensure_integer_roots": True},
        5: {"max_coef": 10, "ensure_integer_roots": True},
        6: {"max_coef": 10, "ensure_integer_roots": False},
        7: {"max_coef": 20, "ensure_integer_roots": False},
        8: {"max_coef": 20, "ensure_integer_roots": False},
        9: {"max_coef": 50, "ensure_integer_roots": False},
        10: {"max_coef": 50, "ensure_integer_roots": False},
    }
    
    def __init__(
        self, 
        a=None, 
        b=None, 
        c=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        max_coef: int = 5,
        ensure_integer_roots: bool = True
    ):
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            max_coef = preset.get("max_coef", max_coef)
            ensure_integer_roots = preset.get("ensure_integer_roots", ensure_integer_roots)
        
        # Генерируем коэффициенты, если не заданы
        if a is None or b is None or c is None:
            a, b, c = self._generate_coefficients(max_coef, ensure_integer_roots)
        
        self.a = a
        self.b = b
        self.c = c
        self.difficulty = difficulty
        
        x = sp.symbols('x')
        eq_expr = self.a*x**2 + self.b*x + self.c
        equation_pretty = sp.pretty(eq_expr)
        description = PROMPT_TEMPLATES["quadratic"]["problem"][language].format(equation_pretty=equation_pretty)
        super().__init__(description, language, detail_level)
    
    @staticmethod
    def _generate_coefficients(max_coef: int, ensure_integer_roots: bool) -> tuple:
        """Генерирует коэффициенты для квадратного уравнения."""
        if ensure_integer_roots:
            # Генерируем целые корни x1, x2 и вычисляем коэффициенты
            # (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
            x1 = random.randint(-max_coef, max_coef)
            x2 = random.randint(-max_coef, max_coef)
            a = 1
            b = -(x1 + x2)
            c = x1 * x2
        else:
            a = random.randint(1, max_coef)
            if random.random() < 0.3:
                a = -a
            b = random.randint(-max_coef, max_coef)
            c = random.randint(-max_coef, max_coef)
        
        return a, b, c

    def solve(self):
        x = sp.symbols('x')
        eq = sp.Eq(self.a*x**2 + self.b*x + self.c, 0)
        eq_pretty = sp.pretty(eq)
        steps = []
        steps.append(PROMPT_TEMPLATES["quadratic"]["step1"][self.language].format(equation_pretty=eq_pretty))
        discriminant = self.b**2 - 4*self.a*self.c
        steps.append(PROMPT_TEMPLATES["quadratic"]["step2"][self.language].format(a=self.a, b=self.b, c=self.c, discriminant=discriminant))
        roots = sp.solve(eq, x)
        steps.append(PROMPT_TEMPLATES["quadratic"]["step3"][self.language].format(roots=roots))
        self.solution_steps.extend(steps)
        self.final_answer = str(roots)

    def get_task_type(self):
        return "quadratic"
