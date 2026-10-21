"""RankingAUCTask — качество ранжирования для бинарных меток.

Оценки попарно различны, поэтому ничьих нет. Согласованная пара — положительный
объект с оценкой строго выше отрицательного. AUC = число таких пар / (n_pos * n_neg),
точная дробь.

Подтипы: ``concordant`` (целое число пар) и ``auc`` (дробь).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def concordant_pairs(items: List[Tuple[int, int]]) -> int:
    """items: (label, score), label 0/1. Оценки уникальны."""
    pos = [s for lab, s in items if lab == 1]
    neg = [s for lab, s in items if lab == 0]
    return sum(1 for p in pos for n in neg if p > n)


class RankingAUCTask(BaseMathTask):
    TASK_TYPE = "ranking_auc"
    TASK_TYPES = ["concordant", "auc"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8}, 9: {"n": 10}, 10: {"n": 10},
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

    def _build(self):
        for _ in range(20):
            labels = [random.randint(0, 1) for _ in range(self.n)]
            if 0 < sum(labels) < self.n:
                break
        else:
            labels = [1, 0] * (self.n // 2) + ([1] if self.n % 2 else [])
        scores = random.sample(range(1, self.n + 5), self.n)
        self.items = list(zip(labels, scores))
        self.n_pos = sum(labels)
        self.n_neg = self.n - self.n_pos
        self.pairs = concordant_pairs(self.items)
        self.auc = Fraction(self.pairs, self.n_pos * self.n_neg)

    def _rows(self) -> str:
        return ", ".join(f"({lab}, {score})" for lab, score in self.items)

    def _descr(self, language):
        data = self._rows()
        rule = ((texts.t('s0', language)))
        if self.task_type == "concordant":
            ask = ((texts.t('s2', language, data=data)))
        else:
            ask = ((texts.t('s3', language, data=data)))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.auc)
        step = ((texts.t('s1', self.language, pairs=self.pairs, n_pos=self.n_pos, n_neg=self.n_neg, shown=shown)))
        ans = str(self.pairs) if self.task_type == "concordant" else shown
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=ans)))]
        self.final_answer = ans

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "concordant":
            return U.verify_int(prediction, self.pairs)
        return verify_fraction(prediction, self.auc)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
