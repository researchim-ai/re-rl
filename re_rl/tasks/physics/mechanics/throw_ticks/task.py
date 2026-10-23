"""ThrowTicksTask — горизонтальный бросок целыми тактами.

За такт вертикальная скорость растёт на 1, высота уменьшается на неё, а по горизонтали прибавляется постоянная скорость.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def throw_trace(height: int, vx: int, ticks: int) -> List[Tuple[int, int, int, int]]:
    y = height
    speed = 0
    x = 0
    land = 0
    span = 0
    trace = []
    for index in range(1, ticks + 1):
        speed += 1
        y -= speed
        x += vx
        if land == 0 and y <= 0:
            land = index
            span = x
        elif land == 0:
            span = x
        trace.append((y, x, land, span))
    return trace


class ThrowTicksTask(BaseMathTask):
    TASK_TYPE = "throw_ticks"
    TASK_TYPES = ["span", "land"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.vx = random.randint(1, 4)
        self.height0 = random.randint(0, self.n * (self.n + 1) // 2)
        self.trace = throw_trace(self.height0, self.vx, self.n)
        _, _, self.land, self.span = self.trace[-1]
        self.answer = self.span if self.task_type == "span" else self.land
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "span" else "s1"
        return texts.t(key, language, height=self.height0, vx=self.vx, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, y=y, x=x, land=land, span=span)
            for index, (y, x, land, span) in enumerate(self.trace, 1)
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
