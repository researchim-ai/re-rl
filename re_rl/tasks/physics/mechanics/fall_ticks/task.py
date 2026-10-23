"""FallTicksTask — свободный полёт целыми тактами.

За такт высота прибавляет текущую скорость, затем скорость падает на 1.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fall_trace(height: int, speed: int, ticks: int) -> List[Tuple[int, int]]:
    trace = []
    for _ in range(ticks):
        height += speed
        speed -= 1
        trace.append((height, speed))
    return trace


class FallTicksTask(BaseMathTask):
    TASK_TYPE = "fall_ticks"
    TASK_TYPES = ["height", "speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 4}, 2: {"n": 2, "v": 6}, 3: {"n": 3, "v": 6},
        4: {"n": 4, "v": 8}, 5: {"n": 5, "v": 8}, 6: {"n": 6, "v": 10},
        7: {"n": 7, "v": 10}, 8: {"n": 8, "v": 12}, 9: {"n": 10, "v": 12},
        10: {"n": 12, "v": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.height0 = random.randint(0, 5)
        self.speed0 = random.randint(0, max(1, int(p["v"])))
        if self.height0 == 0 and self.speed0 == 0:
            self.speed0 = 1
        self.trace = fall_trace(self.height0, self.speed0, self.n)
        self.height, self.speed = self.trace[-1]
        self.answer = self.height if self.task_type == "height" else self.speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "height" else "s1"
        return texts.t(key, language, height=self.height0, speed=self.speed0, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, height=height, speed=speed)
            for index, (height, speed) in enumerate(self.trace, 1)
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
