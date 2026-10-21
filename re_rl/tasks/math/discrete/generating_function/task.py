"""GeneratingFunctionTask — извлечение коэффициента из производящей функции.

Функция выбирается из семейства с известным степенным рядом; коэффициент при
x^n вычисляется через sympy. Ответ — целое число (числовая проверка).
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class GeneratingFunctionTask(BaseMathTask):
    """Найти коэффициент при x^n в разложении производящей функции."""

    TASK_TYPE = "generating_function"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"nmax": 4, "amax": 2}, 2: {"nmax": 5, "amax": 2}, 3: {"nmax": 6, "amax": 3},
        4: {"nmax": 7, "amax": 3}, 5: {"nmax": 8, "amax": 3}, 6: {"nmax": 9, "amax": 4},
        7: {"nmax": 10, "amax": 4}, 8: {"nmax": 11, "amax": 4}, 9: {"nmax": 12, "amax": 5},
        10: {"nmax": 14, "amax": 5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        nmax: Optional[int] = None,
        amax: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.nmax = int(nmax if nmax is not None else preset.get("nmax", 8))
        self.amax = int(amax if amax is not None else preset.get("amax", 3))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._build()
        description = get_template(
            PROMPT_TEMPLATES["generating_function"], "problem", language,
            augment=augment, gf=self._fmt(self._gf), n=self.n,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        x = self.x
        self.n = random.randint(2, self.nmax)
        a = random.randint(1, self.amax)
        kind = random.choice(["geom", "geom_a", "double", "fib"])
        if kind == "geom":
            self._gf = 1 / (1 - x)
        elif kind == "geom_a":
            self._gf = 1 / (1 - a * x)
        elif kind == "double":
            self._gf = 1 / (1 - x) ** 2
        else:
            self._gf = x / (1 - x - x ** 2)
        series = sp.series(self._gf, x, 0, self.n + 1).removeO()
        self._coeff = int(sp.expand(series).coeff(x, self.n))

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["generating_function"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._coeff)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        nums = re.findall(r"-?\d+", extract_answer_text(prediction).replace("−", "-"))
        if not nums:
            return 0.0
        return 1.0 if int(nums[-1]) == self._coeff else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "GeneratingFunctionTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
