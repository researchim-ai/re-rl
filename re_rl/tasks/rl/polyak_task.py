"""PolyakTask — мягкое обновление целевых весов.

θ_new = τ * θ + (1 - τ) * θ_old.
τ — дробь, веса целые, ответ точная дробь.

Подтипы: новое значение одной координаты и приращение θ_new - θ_old.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_TAUS = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 5), Fraction(3, 4)]


def polyak(theta: int, old: int, tau: Fraction) -> Fraction:
    return tau * theta + (1 - tau) * old


class PolyakTask(BaseMathTask):
    TASK_TYPE = "polyak_update"
    TASK_TYPES = ["updated", "delta"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 1, "mag": 4}, 2: {"d": 2, "mag": 5}, 3: {"d": 2, "mag": 6},
        4: {"d": 3, "mag": 6}, 5: {"d": 3, "mag": 8}, 6: {"d": 3, "mag": 8},
        7: {"d": 4, "mag": 10}, 8: {"d": 4, "mag": 10}, 9: {"d": 4, "mag": 12},
        10: {"d": 5, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.dim = int(p["d"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.theta = [random.randint(-self.mag, self.mag) for _ in range(self.dim)]
        self.old = [random.randint(-self.mag, self.mag) for _ in range(self.dim)]
        self.tau = random.choice(_TAUS[:1 + min(3, difficulty // 3)])
        self.updated = [polyak(a, b, self.tau) for a, b in zip(self.theta, self.old)]
        self.index = random.randrange(self.dim)
        self.answer = self.updated[self.index]
        if self.task_type == "delta":
            self.answer = self.updated[self.index] - self.old[self.index]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _vec(self, values: List[int]) -> str:
        return ", ".join(map(str, values))

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"Мягкое обновление: θ_new = τ * θ + (1 - τ) * θ_old, τ = {fmt_fraction(self.tau)}. "
                 f"Координаты нумеруются с 1. Ответ — целое или несократимая дробь.") if ru else
                (f"Soft update: θ_new = τ * θ + (1 - τ) * θ_old, τ = {fmt_fraction(self.tau)}. "
                 f"Coordinates start at 1. Answer with an integer or a reduced fraction."))
        data = ((f"θ = ({self._vec(self.theta)}), θ_old = ({self._vec(self.old)}).") if ru else
                (f"θ = ({self._vec(self.theta)}), θ_old = ({self._vec(self.old)})."))
        if self.task_type == "updated":
            ask = ((f"Найдите координату {self.index + 1} нового вектора.") if ru else
                   (f"Find coordinate {self.index + 1} of the new vector."))
        else:
            ask = ((f"Найдите приращение координаты {self.index + 1}: θ_new - θ_old.") if ru else
                   (f"Find the change of coordinate {self.index + 1}: θ_new - θ_old."))
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Координата {self.index + 1}: новое значение {fmt_fraction(self.updated[self.index])}.")
                if ru else
                (f"Coordinate {self.index + 1}: new value {fmt_fraction(self.updated[self.index])}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
