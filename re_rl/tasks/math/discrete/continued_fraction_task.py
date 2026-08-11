"""ContinuedFractionTask — разложение рационального числа в цепную дробь.

Проверка реконструирует значение из предсказанных неполных частных и сравнивает
с исходной дробью, поэтому принимаются обе эквивалентные записи финального
элемента ([..., a_k] и [..., a_k − 1, 1]).
"""

import math
import random
import re
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ContinuedFractionTask(BaseMathTask):
    """Разложить p/q в конечную цепную дробь."""

    TASK_TYPE = "continued_fraction"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"val_max": 12}, 2: {"val_max": 20}, 3: {"val_max": 30}, 4: {"val_max": 45},
        5: {"val_max": 70}, 6: {"val_max": 100}, 7: {"val_max": 150}, 8: {"val_max": 220},
        9: {"val_max": 320}, 10: {"val_max": 500},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        val_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.val_max = int(val_max if val_max is not None else preset.get("val_max", 70))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["continued_fraction"], "problem", language,
            augment=augment, p=self.p, q=self.q,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.q = random.randint(2, self.val_max)
        self.p = random.randint(2, self.val_max)
        g = math.gcd(self.p, self.q)
        self.p //= g
        self.q //= g
        self._frac = Fraction(self.p, self.q)
        self._coeffs = self._cf(self.p, self.q)

    @staticmethod
    def _cf(p: int, q: int) -> List[int]:
        coeffs = []
        while q != 0:
            coeffs.append(p // q)
            p, q = q, p - (p // q) * q
        return coeffs

    @staticmethod
    def _reconstruct(coeffs: List[int]) -> Optional[Fraction]:
        if not coeffs:
            return None
        try:
            value = Fraction(coeffs[-1])
            for a in reversed(coeffs[:-1]):
                if value == 0:
                    return None
                value = a + Fraction(1) / value
            return value
        except ZeroDivisionError:
            return None

    def solve(self):
        section = PROMPT_TEMPLATES["continued_fraction"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = "[" + "; ".join(str(c) for c in self._coeffs[:1]) + (
            (", " + ", ".join(str(c) for c in self._coeffs[1:])) if len(self._coeffs) > 1 else ""
        ) + "]"
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).replace("−", "-")
        coeffs = [int(t) for t in re.findall(r"-?\d+", text)]
        value = self._reconstruct(coeffs)
        if value is None:
            return 0.0
        return 1.0 if value == self._frac else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ContinuedFractionTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
