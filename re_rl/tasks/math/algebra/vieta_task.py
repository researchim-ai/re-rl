"""VietaTask — формулы Виета: связь корней и коэффициентов многочлена.

Многочлен строится с целыми корнями. Спрашивается сумма или произведение
корней (целое число), проверка числовая.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class VietaTask(BaseMathTask):
    """Формулы Виета: сумма/произведение корней (числовая проверка)."""

    TASK_TYPE = "vieta"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"deg": 2, "root_max": 4}, 2: {"deg": 2, "root_max": 6}, 3: {"deg": 2, "root_max": 8},
        4: {"deg": 3, "root_max": 4}, 5: {"deg": 3, "root_max": 5}, 6: {"deg": 3, "root_max": 6},
        7: {"deg": 4, "root_max": 4}, 8: {"deg": 4, "root_max": 5}, 9: {"deg": 4, "root_max": 6},
        10: {"deg": 5, "root_max": 5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        deg: Optional[int] = None,
        root_max: Optional[int] = None,
        subtype: Optional[str] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.deg = int(deg if deg is not None else preset.get("deg", 3))
        self.root_max = int(root_max if root_max is not None else preset.get("root_max", 5))
        self.subtype = subtype or random.choice(["sum", "product"])
        self.augment = augment

        self.x = sp.Symbol("x")
        self._build()
        description = get_template(
            PROMPT_TEMPLATES["vieta"], "problem", language,
            augment=augment, scenario=self._scenario(language),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.roots: List[int] = [random.randint(-self.root_max, self.root_max) for _ in range(self.deg)]
        poly = sp.Integer(1)
        for r in self.roots:
            poly *= (self.x - r)
        self._poly = sp.expand(poly)
        if self.subtype == "sum":
            self._val = sum(self.roots)
        else:
            p = 1
            for r in self.roots:
                p *= r
            self._val = p
        self._poly_str = sp.sstr(self._poly).replace("**", "^")

    def _scenario(self, language: str) -> str:
        if language == "ru":
            what = "сумму" if self.subtype == "sum" else "произведение"
            return f"Найдите {what} корней многочлена P(x) = {self._poly_str}."
        what = "sum" if self.subtype == "sum" else "product"
        return f"Find the {what} of the roots of the polynomial P(x) = {self._poly_str}."

    def solve(self):
        section = PROMPT_TEMPLATES["vieta"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._val)
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
        return 1.0 if int(nums[-1]) == self._val else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "VietaTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
