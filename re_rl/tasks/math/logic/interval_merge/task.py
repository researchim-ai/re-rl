"""IntervalMergeTask — склейка пересекающихся отрезков.

Отрезки уже упорядочены по левому концу. Соседние целые точки считаются одним куском.
Число отрезков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def merge_trace(intervals: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    pieces = 0
    closed = 0
    start = end = None
    trace = []
    for left, right in intervals:
        if end is None or left > end + 1:
            if end is not None:
                closed += end - start + 1
            pieces += 1
            start, end = left, right
        else:
            end = max(end, right)
        trace.append((pieces, closed + end - start + 1))
    return trace


class IntervalMergeTask(BaseMathTask):
    TASK_TYPE = "interval_merge"
    TASK_TYPES = ["pieces", "cover"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        cursor = 1
        raw = []
        for _ in range(self.n):
            left = cursor + random.randint(0, 2)
            right = left + random.randint(0, 3)
            raw.append((left, right))
            cursor = left + random.randint(1, 3)
        self.intervals = sorted(raw)
        self.trace = merge_trace(self.intervals)
        self.pieces, self.cover = self.trace[-1]
        self.answer = self.pieces if self.task_type == "pieces" else self.cover
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listed = ", ".join(f"{left}-{right}" for left, right in self.intervals)
        key = "s0" if self.task_type == "pieces" else "s1"
        return texts.t(key, language, n=self.n, listed=listed)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, pieces=pieces, cover=cover)
            for index, ((left, right), (pieces, cover)) in enumerate(zip(self.intervals, self.trace), 1)
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
