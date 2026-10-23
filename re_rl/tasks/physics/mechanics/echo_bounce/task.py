"""EchoBounceTask — звук между двумя стенами.

Скорость равна 1. У стены направление меняется на противоположное.
Число ударов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def echo_hits(length: int, start: int, direction: int, count: int) -> List[Tuple[int, int]]:
    position = start
    velocity = direction
    time = 0
    hits = []
    for _ in range(count):
        if velocity > 0:
            time += length - position
            position = length
            wall = length
        else:
            time += position
            position = 0
            wall = 0
        velocity = -velocity
        hits.append((time, wall))
    return hits


class EchoBounceTask(BaseMathTask):
    TASK_TYPE = "echo_bounce"
    TASK_TYPES = ["last", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "L": 6}, 2: {"n": 2, "L": 8}, 3: {"n": 3, "L": 8},
        4: {"n": 3, "L": 10}, 5: {"n": 4, "L": 10}, 6: {"n": 5, "L": 12},
        7: {"n": 6, "L": 12}, 8: {"n": 8, "L": 14}, 9: {"n": 10, "L": 14},
        10: {"n": 12, "L": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.length = max(3, int(p["L"]))
        self.start = random.randint(1, self.length - 1)
        self.direction = random.choice((1, -1))
        self.hits = echo_hits(self.length, self.start, self.direction, self.n)
        self.k = random.randint(1, self.n)
        self.last = self.hits[-1][0]
        self.at_k = self.hits[self.k - 1][0]
        self.answer = self.last if self.task_type == "last" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        way = texts.t("s4" if self.direction > 0 else "s5", language, length=self.length)
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, length=self.length, start=self.start, way=way, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, time=time, wall=wall)
            for index, (time, wall) in enumerate(self.hits, 1)
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
