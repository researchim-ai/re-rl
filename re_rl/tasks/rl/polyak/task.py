"""PolyakTask — мягкое обновление целевых весов.

θ_new = τ * θ + (1 - τ) * θ_old.
τ — дробь, веса целые, ответ точная дробь.

Подтипы: новое значение одной координаты и приращение θ_new - θ_old.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        rule = ((texts.t('s0', language, v0=fmt_fraction(self.tau))))
        data = ((f"θ = ({self._vec(self.theta)}), θ_old = ({self._vec(self.old)})."))
        if self.task_type == "updated":
            ask = ((texts.t('s2', language, v0=self.index + 1)))
        else:
            ask = ((texts.t('s3', language, v0=self.index + 1)))
        return f"{rule} {data} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, v0=self.index + 1, v1=fmt_fraction(self.updated[self.index]))))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
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
