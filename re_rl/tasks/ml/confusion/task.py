"""ConfusionMetricsTask — метрики бинарной классификации.

Подтипы: ``tp``, ``precision``, ``recall``, ``f1``.
Доли считаются точно: precision = tp / (tp + fp), recall = tp / (tp + fn),
F1 = 2 tp / (2 tp + fp + fn). Если знаменатель нулевой, выборка пересобирается.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def counts(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    tp = fp = fn = tn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 1 and p == 0:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


class ConfusionMetricsTask(BaseMathTask):
    TASK_TYPE = "confusion_metrics"
    TASK_TYPES = ["tp", "precision", "recall", "f1"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 6}, 3: {"n": 8}, 4: {"n": 8}, 5: {"n": 10},
        6: {"n": 10}, 7: {"n": 12}, 8: {"n": 12}, 9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _ok(self, c: Dict[str, int]) -> bool:
        if self.task_type == "precision":
            return c["tp"] + c["fp"] > 0
        if self.task_type == "recall":
            return c["tp"] + c["fn"] > 0
        if self.task_type == "f1":
            return 2 * c["tp"] + c["fp"] + c["fn"] > 0
        return True

    def _build(self):
        for _ in range(40):
            self.y_true = [random.randint(0, 1) for _ in range(self.n)]
            self.y_pred = [random.randint(0, 1) for _ in range(self.n)]
            self.c = counts(self.y_true, self.y_pred)
            if self._ok(self.c):
                break
        else:
            self.y_true = [1, 1, 0, 0, 1, 0]
            self.y_pred = [1, 0, 0, 1, 1, 0]
            self.c = counts(self.y_true, self.y_pred)
        tp, fp, fn = self.c["tp"], self.c["fp"], self.c["fn"]
        if self.task_type == "tp":
            self.answer_frac = Fraction(tp)
        elif self.task_type == "precision":
            self.answer_frac = Fraction(tp, tp + fp)
        elif self.task_type == "recall":
            self.answer_frac = Fraction(tp, tp + fn)
        else:
            self.answer_frac = Fraction(2 * tp, 2 * tp + fp + fn)

    def _descr(self, language):
        yt = " ".join(map(str, self.y_true))
        yp = " ".join(map(str, self.y_pred))
        names = {
            "tp": ((texts.t('s2', language))),
            "precision": ((texts.t('s3', language))),
            "recall": ((texts.t('s4', language))),
            "f1": ((texts.t('s5', language))),
        }[self.task_type]
        extra = texts.t("s6", language) if self.task_type != "tp" else ""
        return ((texts.t('s0', language, yt=yt, yp=yp, names=names, extra=extra)))

    def solve(self):
        c = self.c
        shown = fmt_fraction(self.answer_frac)
        step = ((texts.t('s1', self.language, v0=c['tp'], v1=c['fp'], v2=c['fn'], v3=c['tn'], shown=shown)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "tp":
            return U.verify_int(prediction, int(self.answer_frac))
        return verify_fraction(prediction, self.answer_frac)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
