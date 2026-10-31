"""MaeTask — средняя и суммарная абсолютная ошибка.

Прогнозы и истинные значения целые, ответ — точная дробь.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def absolute_errors(pred: List[int], truth: List[int]) -> Tuple[Fraction, Fraction]:
    total = sum(abs(Fraction(hat) - Fraction(value)) for hat, value in zip(pred, truth))
    return total / len(pred), total


class MaeTask(BaseMathTask):
    TASK_TYPE = "mae_loss"
    TASK_TYPES = ["mae", "sae"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 4}, 2: {"n": 2, "mag": 5}, 3: {"n": 3, "mag": 5},
        4: {"n": 3, "mag": 6}, 5: {"n": 4, "mag": 6}, 6: {"n": 4, "mag": 8},
        7: {"n": 5, "mag": 8}, 8: {"n": 5, "mag": 10}, 9: {"n": 6, "mag": 10},
        10: {"n": 6, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.pred = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.truth = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.mae, self.sae = absolute_errors(self.pred, self.truth)
        self.answer = self.mae if self.task_type == "mae" else self.sae
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        pred = ", ".join(map(str, self.pred))
        truth = ", ".join(map(str, self.truth))
        data = ((texts.t('s0', language, pred=pred, truth=truth)))
        if self.task_type == "mae":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{data} {ask}"

    def solve(self):
        from re_rl.tasks.ml.detailed_solvers import solve_detailed
        solve_detailed(self)

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
