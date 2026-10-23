"""CoverPointTask — сколько отрезков накрывает точку.

Отрезки замкнутые. Первый — с наименьшим номером в списке. Ноль, если точка свободна.
Число отрезков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Interval = Tuple[int, int]


def cover_trace(intervals: Sequence[Interval], point: int) -> List[Tuple[int, int]]:
    count = 0
    first = 0
    trace = []
    for left, right in intervals:
        if left <= point <= right:
            count += 1
            if first == 0:
                first = len(trace) + 1
        trace.append((count, first))
    return trace


class CoverPointTask(BaseMathTask):
    TASK_TYPE = "cover_point"
    TASK_TYPES = ["count", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.intervals = []
        for _ in range(self.n):
            left = random.randint(0, 8)
            right = left + random.randint(0, 4)
            self.intervals.append((left, right))
        self.point = random.randint(0, 10)
        self.trace = cover_trace(self.intervals, self.point)
        self.count, self.first = self.trace[-1]
        self.answer = self.count if self.task_type == "count" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{left} {right}" for left, right in self.intervals)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, point=self.point, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, count=count, first=first)
            for index, (count, first) in enumerate(self.trace, 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
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
