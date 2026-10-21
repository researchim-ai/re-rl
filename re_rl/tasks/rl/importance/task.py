"""ImportanceRatioTask — произведение пошаговых отношений важности.

На каждом шаге даны два положительных целых: числитель политики и знаменатель поведения.
Ответ — произведение дробей либо число шагов, где числитель строго больше знаменателя.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def importance_product(pairs: List[Tuple[int, int]]) -> Tuple[Fraction, int]:
    product = Fraction(1)
    above = 0
    for numer, denom in pairs:
        product *= Fraction(numer, denom)
        if numer > denom:
            above += 1
    return product, above


class ImportanceRatioTask(BaseMathTask):
    TASK_TYPE = "importance_ratio"
    TASK_TYPES = ["product", "above"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 3}, 2: {"n": 2, "mag": 4}, 3: {"n": 3, "mag": 4},
        4: {"n": 3, "mag": 5}, 5: {"n": 3, "mag": 6}, 6: {"n": 4, "mag": 6},
        7: {"n": 4, "mag": 7}, 8: {"n": 5, "mag": 7}, 9: {"n": 5, "mag": 8},
        10: {"n": 6, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.pairs = [
            (random.randint(1, self.mag), random.randint(1, self.mag))
            for _ in range(self.count)
        ]
        self.product, self.above = importance_product(self.pairs)
        self.answer = self.product if self.task_type == "product" else Fraction(self.above)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return ", ".join(f"{numer}/{denom}" for numer, denom in self.pairs)

    def _descr(self, language):
        data = ((texts.t('s0', language, v0=self._shown())))
        if self.task_type == "product":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{data} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, v0=fmt_fraction(self.product), above=self.above)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "above":
            return U.verify_int(prediction, self.above)
        return verify_fraction(prediction, self.product)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
