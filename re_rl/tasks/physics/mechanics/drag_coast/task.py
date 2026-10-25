"""DragCoastTask — разгон с сопротивлением, пропорциональным скорости.

За такт снимается целая доля скорости и прибавляется тяга. Счёт идёт целыми числами SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def drag_trace(speed: int, thrust: int, divisor: int, ticks: int) -> List[Tuple[int, int]]:
    velocity = sp.Integer(speed)
    push = sp.Integer(thrust)
    lost = sp.Integer(0)
    trace = []
    for _ in range(ticks):
        drag = velocity // divisor
        lost += drag
        velocity = velocity + push - drag
        trace.append((int(velocity), int(lost)))
    return trace


class DragCoastTask(BaseMathTask):
    TASK_TYPE = "drag_coast"
    TASK_TYPES = ["speed", "lost"]
    DIVISOR = 2

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
        self.speed = random.randint(0, 6)
        self.thrust = random.randint(1, 4)
        self.trace = drag_trace(self.speed, self.thrust, self.DIVISOR, self.n)
        self.final_speed = self.trace[-1][0]
        self.lost = self.trace[-1][1]
        self.answer = self.final_speed if self.task_type == "speed" else self.lost
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "speed" else "s1"
        return texts.t(
            key, language, n=self.n, speed=self.speed, thrust=self.thrust, divisor=self.DIVISOR,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, lost=lost)
            for index, (speed, lost) in enumerate(self.trace, 1)
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
