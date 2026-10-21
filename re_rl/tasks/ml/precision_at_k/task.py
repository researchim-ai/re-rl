"""PrecisionAtKTask — сколько релевантных объектов в топ-k и сама точность.

При равной оценке выше стоит объект левее. Точность — точная дробь hits/k.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def topk_hits(scores: List[int], labels: List[int], k: int) -> int:
    order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return sum(labels[i] for i in order[:k])


class PrecisionAtKTask(BaseMathTask):
    TASK_TYPE = "precision_at_k"
    TASK_TYPES = ["hits", "precision"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 4}, 2: {"n": 4, "mag": 5}, 3: {"n": 4, "mag": 5},
        4: {"n": 5, "mag": 6}, 5: {"n": 6, "mag": 6}, 6: {"n": 7, "mag": 8},
        7: {"n": 8, "mag": 8}, 8: {"n": 9, "mag": 10}, 9: {"n": 10, "mag": 10},
        10: {"n": 12, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.scores = [random.randint(0, self.mag) for _ in range(self.n)]
        self.labels = [random.randint(0, 1) for _ in range(self.n)]
        self.k = random.randint(1, self.n)
        self.hits = topk_hits(self.scores, self.labels, self.k)
        self.precision = Fraction(self.hits, self.k)
        self.answer = Fraction(self.hits) if self.task_type == "hits" else self.precision
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pairs(self) -> str:
        return ", ".join(f"({score}, {label})" for score, label in zip(self.scores, self.labels))

    def _descr(self, language):
        rule = ((texts.t('s0', language, v0=self._pairs(), k=self.k)))
        if self.task_type == "hits":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, k=self.k, hits=self.hits, v2=fmt_fraction(self.precision))))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "hits":
            return U.verify_int(prediction, self.hits)
        return verify_fraction(prediction, self.precision)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
