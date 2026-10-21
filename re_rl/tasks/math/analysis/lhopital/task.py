"""LHopitalTask — вычисление предела неопределённости 0/0 (правило Лопиталя).

Все выражения строятся так, что подстановка точки даёт неопределённость 0/0,
а предел — конечное рациональное число. Проверка числовая.
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class LHopitalTask(BaseMathTask):
    """Предел неопределённости через правило Лопиталя (числовой ответ)."""

    TASK_TYPE = "lhopital"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"kmax": 2}, 2: {"kmax": 3}, 3: {"kmax": 3}, 4: {"kmax": 4},
        5: {"kmax": 4}, 6: {"kmax": 5}, 7: {"kmax": 5}, 8: {"kmax": 6},
        9: {"kmax": 7}, 10: {"kmax": 8},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        kmax: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.kmax = int(kmax if kmax is not None else preset.get("kmax", 4))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._build()

        description = get_template(
            PROMPT_TEMPLATES["lhopital"], "problem", language,
            augment=augment, expr=self._fmt(self._expr), point=self._point_str,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        x = self.x
        k = random.randint(1, self.kmax)
        m = random.randint(1, self.kmax)
        kind = random.choice(["sin", "exp", "cos", "log", "poly"])
        if kind == "sin":
            self._expr = sp.sin(k * x) / (m * x)
            self._point = sp.Integer(0)
        elif kind == "exp":
            self._expr = (sp.exp(k * x) - 1) / (m * x)
            self._point = sp.Integer(0)
        elif kind == "cos":
            self._expr = (1 - sp.cos(k * x)) / (x ** 2)
            self._point = sp.Integer(0)
        elif kind == "log":
            self._expr = sp.log(1 + k * x) / (m * x)
            self._point = sp.Integer(0)
        else:
            c = random.randint(1, self.kmax)
            self._expr = (x ** 2 - c ** 2) / (x - c)
            self._point = sp.Integer(c)
        self._point_str = str(self._point)
        self._limit = sp.limit(self._expr, x, self._point)

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["lhopital"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._limit)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], [float(self._limit)]) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "LHopitalTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
