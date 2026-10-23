"""EpsScheduleTask — порог исследования уменьшается на каждом шаге.

Пока случайное число строго меньше порога, берётся исследовательское действие.
После шага порог падает на 1, но не ниже нуля. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int, int]


def eps_trace(rows: Sequence[Row], start: int) -> List[Tuple[int, int, int, int]]:
    threshold = start
    explores = 0
    trace = []
    for draw, explore, greedy in rows:
        if draw < threshold:
            action = explore
            explores += 1
            kind = 1
        else:
            action = greedy
            kind = 0
        trace.append((threshold, action, kind, explores))
        if threshold > 0:
            threshold -= 1
    return trace


class EpsScheduleTask(BaseMathTask):
    TASK_TYPE = "eps_schedule"
    TASK_TYPES = ["explores", "taken"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "t": 6}, 2: {"n": 4, "t": 6}, 3: {"n": 5, "t": 6},
        4: {"n": 6, "t": 7}, 5: {"n": 7, "t": 7}, 6: {"n": 8, "t": 8},
        7: {"n": 9, "t": 8}, 8: {"n": 10, "t": 8}, 9: {"n": 12, "t": 9},
        10: {"n": 14, "t": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = max(0, int(p["t"]))
        self.rows = [
            (random.randint(0, 9), random.randint(1, 4), random.randint(1, 4))
            for _ in range(self.n)
        ]
        self.trace = eps_trace(self.rows, self.start)
        self.k = random.randint(1, self.n)
        self.explores = self.trace[-1][3]
        self.taken = self.trace[self.k - 1][1]
        self.answer = self.explores if self.task_type == "explores" else self.taken
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{draw}, {explore}, {greedy}" for draw, explore, greedy in self.rows
        )
        key = "s0" if self.task_type == "explores" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, draw=draw, threshold=threshold,
                action=action, kind=kind, explores=explores,
            )
            for index, ((draw, _, _), (threshold, action, kind, explores)) in enumerate(
                zip(self.rows, self.trace), 1,
            )
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
