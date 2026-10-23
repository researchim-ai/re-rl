"""FloorRunTask — лифт едет к остановкам по очереди.

Каждая остановка добавляет модуль разности этажей. Число остановок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def floor_trace(start: int, stops: Sequence[int]) -> List[Tuple[int, int]]:
    floor = start
    distance = 0
    trace = []
    for stop in stops:
        distance += abs(stop - floor)
        floor = stop
        trace.append((floor, distance))
    return trace


class FloorRunTask(BaseMathTask):
    TASK_TYPE = "floor_run"
    TASK_TYPES = ["distance", "floor"]

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
        self.start = random.randint(1, 5)
        self.stops = [random.randint(1, 8) for _ in range(self.n)]
        self.trace = floor_trace(self.start, self.stops)
        self.floor, self.distance = self.trace[-1]
        self.answer = self.distance if self.task_type == "distance" else self.floor
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(stop) for stop in self.stops)
        key = "s0" if self.task_type == "distance" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, floor=floor, distance=distance)
            for index, (floor, distance) in enumerate(self.trace, 1)
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
