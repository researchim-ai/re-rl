"""PartialDerivativesTask — частная производная функции двух переменных.

Проверка символическая (sympy): любое выражение, тождественно равное эталонной
частной производной, засчитывается.
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class PartialDerivativesTask(BaseMathTask):
    """Найти ∂f/∂x или ∂f/∂y (проверка через sympy)."""

    TASK_TYPE = "partial_derivatives"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"terms": 2, "max_pow": 2, "trig": False},
        2: {"terms": 2, "max_pow": 2, "trig": False},
        3: {"terms": 3, "max_pow": 2, "trig": False},
        4: {"terms": 3, "max_pow": 3, "trig": False},
        5: {"terms": 3, "max_pow": 3, "trig": True},
        6: {"terms": 4, "max_pow": 3, "trig": True},
        7: {"terms": 4, "max_pow": 4, "trig": True},
        8: {"terms": 4, "max_pow": 4, "trig": True},
        9: {"terms": 5, "max_pow": 4, "trig": True},
        10: {"terms": 5, "max_pow": 5, "trig": True},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        terms: Optional[int] = None,
        max_pow: Optional[int] = None,
        trig: Optional[bool] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.terms = int(terms if terms is not None else preset.get("terms", 3))
        self.max_pow = int(max_pow if max_pow is not None else preset.get("max_pow", 3))
        self.trig = bool(trig if trig is not None else preset.get("trig", True))
        self.augment = augment

        self.x, self.y = sp.symbols("x y")
        self._func = self._make_function()
        self.var = random.choice(["x", "y"])
        self._ref_expr = sp.diff(self._func, sp.Symbol(self.var))

        description = get_template(
            PROMPT_TEMPLATES["partial_derivatives"], "problem", language,
            augment=augment, func=self._fmt(self._func), var=self.var,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _make_function(self) -> sp.Expr:
        x, y = self.x, self.y
        expr = sp.Integer(0)
        for _ in range(self.terms):
            c = random.randint(1, 5)
            px = random.randint(0, self.max_pow)
            py = random.randint(0, self.max_pow)
            expr += c * x ** px * y ** py
        if self.trig and random.random() < 0.6:
            expr += random.choice([sp.sin(x * y), sp.cos(x + y), sp.exp(x) * y])
        return sp.expand(expr) if not self.trig else expr

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["partial_derivatives"]
        self.solution_steps.append(
            get_template(section, "step_setup", self.language, augment=False, var=self.var)
        )
        result = self._fmt(self._ref_expr)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import sympy_equiv

        if self.final_answer is None:
            self.solve()
        return sympy_equiv(prediction, self._ref_expr, ["x", "y"])

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "PartialDerivativesTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
