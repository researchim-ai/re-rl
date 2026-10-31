"""MajorityTask — элемент, который встречается строго больше n/2 раз.

Такой элемент в выборке ровно один.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def majority(values: List[int]) -> int:
    counts: Dict[int, int] = {}
    need = len(values) // 2 + 1
    for value in values:
        counts[value] = counts.get(value, 0) + 1
        if counts[value] >= need:
            return value
    raise RuntimeError(texts.literal('literals.s2'))


class MajorityTask(BaseMathTask):
    TASK_TYPE = "majority_element"
    TASK_TYPES = ["element"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 5}, 2: {"n": 5, "mag": 6}, 3: {"n": 5, "mag": 8},
        4: {"n": 7, "mag": 8}, 5: {"n": 7, "mag": 10}, 6: {"n": 9, "mag": 10},
        7: {"n": 9, "mag": 12}, 8: {"n": 11, "mag": 12}, 9: {"n": 13, "mag": 15},
        10: {"n": 15, "mag": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "element"
        self.augment = augment
        self.answer = random.randint(0, self.mag)
        need = self.n // 2 + 1
        others = [random.randint(0, self.mag) for _ in range(self.n - need)]
        self.values = [self.answer] * need + others
        random.shuffle(self.values)
        if majority(self.values) != self.answer:
            raise RuntimeError(texts.t('s3', language))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.values))
        return ((texts.t('s0', language, data=data)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
