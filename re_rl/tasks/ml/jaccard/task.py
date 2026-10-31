"""JaccardTask — индекс Жаккара двух бинарных векторов.

J = |A ∩ B| / |A ∪ B|. Хотя бы в одной позиции стоит единица, поэтому знаменатель ненулевой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def jaccard_parts(left: List[int], right: List[int]) -> Tuple[Fraction, int, int]:
    intersection = sum(a and b for a, b in zip(left, right))
    union = sum(a or b for a, b in zip(left, right))
    return Fraction(intersection, union), intersection, union


class JaccardTask(BaseMathTask):
    TASK_TYPE = "jaccard_index"
    TASK_TYPES = ["index", "intersection"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 4}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.left = [random.randint(0, 1) for _ in range(self.n)]
        self.right = [random.randint(0, 1) for _ in range(self.n)]
        if not any(a or b for a, b in zip(self.left, self.right)):
            self.left[0] = 1
        self.index, self.intersection, self.union = jaccard_parts(self.left, self.right)
        self.answer = self.index if self.task_type == "index" else Fraction(self.intersection)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _bits(self, values: List[int]) -> str:
        return " ".join(map(str, values))

    def _descr(self, language):
        data = ((texts.t('s0', language, v0=self._bits(self.left), v1=self._bits(self.right))))
        if self.task_type == "index":
            ask = ((texts.t('s2', language)))
        else:
            ask = (((texts.t('s3', language))))
        return f"{data} {ask}"

    def solve(self):
        from re_rl.tasks.ml.detailed_solvers import solve_detailed
        solve_detailed(self)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "intersection":
            return U.verify_int(prediction, self.intersection)
        return verify_fraction(prediction, self.index)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
