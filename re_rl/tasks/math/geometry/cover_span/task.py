"""CoverSpanTask — длина объединения отрезков и наибольшая глубина.

Отрезки замкнутые. Длина — мера объединения, общая точка сама по себе длину не добавляет.
В конце отрезка он ещё покрывает точку, поэтому стык увеличивает глубину.
Число отрезков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Interval = Tuple[int, int]


def sweep_cover(intervals: Sequence[Interval]) -> Tuple[int, int]:
    events = []
    for left, right in intervals:
        events.append((left, 1))
        events.append((right, -1))
    events.sort(key=lambda item: (item[0], 0 if item[1] > 0 else 1))
    covered = 0
    depth = 0
    max_depth = 0
    prev = None
    index = 0
    while index < len(events):
        pos = events[index][0]
        if prev is not None and depth > 0:
            covered += pos - prev
        while index < len(events) and events[index][0] == pos and events[index][1] > 0:
            depth += 1
            index += 1
        if depth > max_depth:
            max_depth = depth
        while index < len(events) and events[index][0] == pos and events[index][1] < 0:
            depth -= 1
            index += 1
        prev = pos
    return covered, max_depth


def cover_trace(intervals: Sequence[Interval]) -> List[Tuple[int, int]]:
    return [sweep_cover(intervals[:index]) for index in range(1, len(intervals) + 1)]


class CoverSpanTask(BaseMathTask):
    TASK_TYPE = "cover_span"
    TASK_TYPES = ["length", "depth"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "span": 6, "width": 3}, 2: {"n": 2, "span": 8, "width": 4},
        3: {"n": 3, "span": 8, "width": 4}, 4: {"n": 4, "span": 10, "width": 4},
        5: {"n": 5, "span": 12, "width": 5}, 6: {"n": 6, "span": 14, "width": 5},
        7: {"n": 7, "span": 16, "width": 6}, 8: {"n": 8, "span": 18, "width": 6},
        9: {"n": 10, "span": 22, "width": 7}, 10: {"n": 12, "span": 28, "width": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        span = max(self.n + 2, int(p["span"]))
        width = max(2, int(p["width"]))
        self.intervals = []
        for _ in range(self.n):
            left = random.randint(0, span - 1)
            right = random.randint(left + 1, min(span, left + width))
            self.intervals.append((left, right))
        self.trace = cover_trace(self.intervals)
        self.length, self.depth = self.trace[-1]
        self.answer = self.length if self.task_type == "length" else self.depth
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{left}-{right}" for left, right in self.intervals)
        key = "s0" if self.task_type == "length" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, length=length, depth=depth)
            for index, ((left, right), (length, depth)) in enumerate(zip(self.intervals, self.trace), 1)
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
