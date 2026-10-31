"""ReciprocalRankTask — обратный ранг первого релевантного объекта.

Метки уже стоят от лучшей оценки к худшей. Ранг — позиция первой единицы, с 1.
Обратный ранг равен 1/ранг. В списке есть хотя бы одна единица.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def reciprocal_rank(labels: List[int]) -> Tuple[Fraction, int]:
    rank = labels.index(1) + 1
    return Fraction(1, rank), rank


class ReciprocalRankTask(BaseMathTask):
    TASK_TYPE = "reciprocal_rank"
    TASK_TYPES = ["reciprocal", "rank"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 4}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.labels = [random.randint(0, 1) for _ in range(self.n)]
        if 1 not in self.labels:
            self.labels[random.randrange(self.n)] = 1
        self.reciprocal, self.rank = reciprocal_rank(self.labels)
        self.answer = self.reciprocal if self.task_type == "reciprocal" else Fraction(self.rank)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = " ".join(map(str, self.labels))
        rule = ((texts.t('s0', language, shown=shown)))
        if self.task_type == "reciprocal":
            ask = ((texts.t('s2', language)))
        else:
            ask = (((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.ml.detailed_solvers import solve_detailed
        solve_detailed(self)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "rank":
            return U.verify_int(prediction, self.rank)
        return verify_fraction(prediction, self.reciprocal)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
