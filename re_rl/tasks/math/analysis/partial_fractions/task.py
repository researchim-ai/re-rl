"""PartialFractionsTask — разложение рациональной дроби на простейшие.

Проверка символическая: засчитывается любое выражение, тождественно равное
исходной дроби (в частности, корректное разложение на простейшие).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class PartialFractionsTask(BaseMathTask):
    """Разложить рациональную дробь на простейшие (проверка через sympy)."""

    TASK_TYPE = "partial_fractions"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_factors": 2, "max_root": 3, "num_deg": 0},
        2: {"num_factors": 2, "max_root": 4, "num_deg": 0},
        3: {"num_factors": 2, "max_root": 5, "num_deg": 1},
        4: {"num_factors": 2, "max_root": 6, "num_deg": 1},
        5: {"num_factors": 3, "max_root": 5, "num_deg": 1},
        6: {"num_factors": 3, "max_root": 6, "num_deg": 1},
        7: {"num_factors": 3, "max_root": 7, "num_deg": 2},
        8: {"num_factors": 4, "max_root": 6, "num_deg": 2},
        9: {"num_factors": 4, "max_root": 7, "num_deg": 2},
        10: {"num_factors": 4, "max_root": 8, "num_deg": 3},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_factors: Optional[int] = None,
        max_root: Optional[int] = None,
        num_deg: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_factors = int(num_factors if num_factors is not None else preset.get("num_factors", 2))
        self.max_root = int(max_root if max_root is not None else preset.get("max_root", 5))
        self.num_deg = int(num_deg if num_deg is not None else preset.get("num_deg", 1))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._orig = self._make_fraction()
        self._decomposed = sp.apart(self._orig, self.x)

        description = get_template(
            PROMPT_TEMPLATES["partial_fractions"], "problem", language,
            augment=augment, expr=self._fmt(self._orig),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _make_fraction(self) -> sp.Expr:
        x = self.x
        roots: List[int] = []
        while len(roots) < self.num_factors:
            r = random.randint(-self.max_root, self.max_root)
            if r not in roots:
                roots.append(r)
        den = sp.Integer(1)
        for r in roots:
            den *= (x - r)
        den = sp.expand(den)
        # Числитель степени < степени знаменателя, чтобы дробь была правильной.
        deg = min(self.num_deg, self.num_factors - 1)
        coeffs = [random.randint(-5, 5) for _ in range(deg + 1)]
        if all(c == 0 for c in coeffs):
            coeffs[0] = random.randint(1, 5)
        num = sum(c * x ** i for i, c in enumerate(coeffs))
        return sp.nsimplify(num) / den

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["partial_fractions"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._fmt(self._decomposed)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import parse_expr, extract_answer_text

        if self.final_answer is None:
            self.solve()
        expr = parse_expr(extract_answer_text(prediction), ["x"])
        if expr is None:
            return 0.0
        try:
            return 1.0 if sp.simplify(expr - self._orig) == 0 else 0.0
        except Exception:
            return 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "PartialFractionsTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
