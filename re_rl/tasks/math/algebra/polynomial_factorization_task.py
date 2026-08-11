"""PolynomialFactorizationTask — разложение многочлена на множители.

Многочлен генерируется как произведение множителей с целыми корнями, затем
раскрывается. Нужно вернуть разложение. Проверка — символическая (sympy):
засчитывается любое выражение, алгебраически эквивалентное исходному многочлену.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class PolynomialFactorizationTask(BaseMathTask):
    """Разложить многочлен на множители (проверка через sympy)."""

    TASK_TYPE = "polynomial_factorization"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_factors": 2, "max_root": 3, "lead": 1},
        2: {"num_factors": 2, "max_root": 4, "lead": 1},
        3: {"num_factors": 2, "max_root": 5, "lead": 1},
        4: {"num_factors": 3, "max_root": 4, "lead": 1},
        5: {"num_factors": 3, "max_root": 5, "lead": 1},
        6: {"num_factors": 3, "max_root": 6, "lead": 2},
        7: {"num_factors": 4, "max_root": 5, "lead": 1},
        8: {"num_factors": 4, "max_root": 6, "lead": 2},
        9: {"num_factors": 4, "max_root": 7, "lead": 2},
        10: {"num_factors": 5, "max_root": 6, "lead": 2},
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
        lead: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_factors = int(num_factors if num_factors is not None else preset.get("num_factors", 3))
        self.max_root = int(max_root if max_root is not None else preset.get("max_root", 5))
        self.lead = int(lead if lead is not None else preset.get("lead", 1))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._expanded = self._make_polynomial()
        self._factored = sp.factor(self._expanded)

        description = get_template(
            PROMPT_TEMPLATES["polynomial_factorization"], "problem", language,
            augment=augment, poly=self._format_expr(self._expanded),
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_polynomial(self) -> sp.Expr:
        roots = [random.randint(-self.max_root, self.max_root) for _ in range(self.num_factors)]
        lead = random.choice([1, self.lead]) if self.lead > 1 else 1
        expr = sp.Integer(lead)
        for r in roots:
            expr *= (self.x - r)
        return sp.expand(expr)

    def _format_expr(self, expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["polynomial_factorization"]
        result = self._format_expr(self._factored)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip().split("=")[-1].strip().rstrip(".").replace("^", "**")
        try:
            expr = sp.sympify(text, locals={"x": self.x})
        except (sp.SympifyError, SyntaxError, TypeError, ValueError):
            return 0.0
        try:
            return 1.0 if sp.simplify(expr - self._expanded) == 0 else 0.0
        except Exception:
            return 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "PolynomialFactorizationTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
