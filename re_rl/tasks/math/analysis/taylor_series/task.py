"""TaylorSeriesTask — разложение функции в ряд Тейлора/Маклорена до порядка n.

Проверка символическая (sympy): засчитывается любое выражение, тождественно
равное эталонному многочлену Тейлора.
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class TaylorSeriesTask(BaseMathTask):
    """Найти многочлен Тейлора функции в точке x=0."""

    TASK_TYPE = "taylor_series"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"order": 2}, 2: {"order": 2}, 3: {"order": 3}, 4: {"order": 3},
        5: {"order": 4}, 6: {"order": 4}, 7: {"order": 5}, 8: {"order": 5},
        9: {"order": 6}, 10: {"order": 7},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        order: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.order = int(order if order is not None else preset.get("order", 4))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._func = self._pick_function()
        series = sp.series(self._func, self.x, 0, self.order + 1).removeO()
        self._ref_expr = sp.expand(series)

        description = get_template(
            PROMPT_TEMPLATES["taylor_series"], "problem", language,
            augment=augment, func=self._fmt(self._func), order=self.order,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _pick_function(self) -> sp.Expr:
        x = self.x
        k = random.randint(1, 3)
        catalog = [
            sp.sin(k * x), sp.cos(k * x), sp.exp(k * x),
            sp.log(1 + x), 1 / (1 - k * x), sp.sin(x) * sp.cos(x),
        ]
        return random.choice(catalog)

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["taylor_series"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._fmt(self._ref_expr)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import sympy_equiv

        if self.final_answer is None:
            self.solve()
        return sympy_equiv(prediction, self._ref_expr, ["x"])

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "TaylorSeriesTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
