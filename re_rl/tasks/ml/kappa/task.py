"""CohenKappaTask — каппа Коэна по четырём клеткам бинарной матрицы ошибок.

po = (TP + TN) / n.
pe = ((TP+FP)(TP+FN) + (TN+FN)(TN+FP)) / n^2.
κ = (po - pe) / (1 - pe). Генератор не выпускает случаи pe = 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def cohen_parts(tp: int, fp: int, fn: int, tn: int) -> Optional[Tuple[Fraction, Fraction]]:
    n = tp + fp + fn + tn
    if n == 0:
        return None
    po = Fraction(tp + tn, n)
    pe = Fraction((tp + fp) * (tp + fn) + (tn + fn) * (tn + fp), n * n)
    if pe == 1:
        return None
    return (po - pe) / (1 - pe), po


class CohenKappaTask(BaseMathTask):
    TASK_TYPE = "cohen_kappa"
    TASK_TYPES = ["kappa", "agreement"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 2}, 2: {"m": 3}, 3: {"m": 3}, 4: {"m": 4}, 5: {"m": 4},
        6: {"m": 5}, 7: {"m": 6}, 8: {"m": 6}, 9: {"m": 8}, 10: {"m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        parts = None
        for _ in range(40):
            self.tp = random.randint(0, self.mag)
            self.fp = random.randint(0, self.mag)
            self.fn = random.randint(0, self.mag)
            self.tn = random.randint(0, self.mag)
            parts = cohen_parts(self.tp, self.fp, self.fn, self.tn)
            if parts is not None:
                break
        if parts is None:
            self.tp, self.fp, self.fn, self.tn = 1, 0, 0, 1
            parts = cohen_parts(1, 0, 0, 1)
        self.kappa, self.agreement = parts
        self.answer = self.kappa if self.task_type == "kappa" else self.agreement
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        cells = texts.t('s3', language, tp=self.tp, fp=self.fp, fn=self.fn, tn=self.tn)
        rule = ((texts.t('s0', language, cells=cells)))
        ask = (((texts.t('s1', language))) if self.task_type == "kappa" else
               ((texts.t('s2', language))))
        return f"{rule} {ask}"

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
