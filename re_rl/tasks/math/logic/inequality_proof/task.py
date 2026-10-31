"""InequalityProofTask — верно ли, что квадратичное выражение неотрицательно ∀x.

Даётся выражение a·x² + b·x + c; нужно определить, выполнено ли ``≥ 0`` для всех
действительных x. Задача полностью решаема аналитически (знак старшего
коэффициента и дискриминант), поэтому эталон однозначен. Ответ YES/NO.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from math import isqrt
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class InequalityProofTask(BaseMathTask):
    """Неотрицательность квадратного трёхчлена при всех x (YES/NO)."""

    TASK_TYPE = "inequality_proof"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coeff": 3},
        2: {"max_coeff": 4},
        3: {"max_coeff": 5},
        4: {"max_coeff": 6},
        5: {"max_coeff": 7},
        6: {"max_coeff": 8},
        7: {"max_coeff": 10},
        8: {"max_coeff": 12},
        9: {"max_coeff": 15},
        10: {"max_coeff": 20},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        max_coeff: Optional[int] = None,
        a=None, b=None, c=None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.max_coeff = max_coeff if max_coeff is not None else preset["max_coeff"]
        if type(self.max_coeff) is not int or not 1 <= self.max_coeff <= 1_000_000:
            raise ValueError("invalid_max_coeff")
        self.augment = augment

        self.x = sp.Symbol("x")
        if all(v is None for v in (a,b,c)):
            self.a, self.b, self.c = self._make_coeffs()
        elif all(type(v) is int for v in (a,b,c)):
            self.a,self.b,self.c=a,b,c
        else:raise ValueError("invalid_coefficients")
        self._always_nonneg = self._decide()

        expr = self.a * self.x ** 2 + self.b * self.x + self.c
        expr_str = sp.sstr(sp.expand(expr)).replace("**", "^")
        description = get_template(
            PROMPT_TEMPLATES["inequality_proof"], "problem", language,
            augment=augment, expr=expr_str,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_coeffs(self):
        bound=self.max_coeff
        if random.random()<0.5:
            a=random.randint(1,bound)
            limit=min(bound,isqrt(4*a*bound))
            b=random.randint(-limit,limit)
            minimum=(b*b+4*a-1)//(4*a)
            return a,b,random.randint(minimum,bound)
        return tuple(random.randint(-bound,bound) for _ in range(3))

    def _decide(self) -> bool:
        # a x^2 + b x + c >= 0 для всех x  <=>  (a>0 и D<=0) или (a==0,b==0,c>=0)
        a, b, c = self.a, self.b, self.c
        if a == 0:
            return b == 0 and c >= 0
        disc = b * b - 4 * a * c
        return a > 0 and disc <= 0

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        from re_rl.tasks.math.logic.proof_semantics import verify_boolean
        self.solve()
        return verify_boolean(prediction,self.final_answer=="YES")

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "InequalityProofTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
