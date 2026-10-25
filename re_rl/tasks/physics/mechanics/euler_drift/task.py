"""EulerDriftTask — полунеявный Эйлер против точной координаты.

Скорость получает ускорение до сдвига координаты. Точная формула берётся через рациональные числа SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def euler_trace(place: int, speed: int, accel: int, ticks: int) -> List[Tuple[int, int, int]]:
    coord = sp.Integer(place)
    velocity = sp.Integer(speed)
    acceleration = sp.Integer(accel)
    trace = []
    for step in range(1, ticks + 1):
        velocity += acceleration
        coord += velocity
        exact = (
            sp.Integer(place)
            + sp.Integer(speed) * step
            + sp.Rational(accel, 2) * step ** 2
        )
        gap = sp.Integer(2) * coord - sp.together(sp.Integer(2) * exact)
        trace.append((int(velocity), int(coord), int(gap)))
    return trace


class EulerDriftTask(BaseMathTask):
    TASK_TYPE = "euler_drift"
    TASK_TYPES = ["place", "gap"]

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
        self.place = random.randint(0, 4)
        self.speed = random.randint(-2, 4)
        self.accel = random.choice([-3, -2, -1, 1, 2, 3])
        self.trace = euler_trace(self.place, self.speed, self.accel, self.n)
        self.final_place = self.trace[-1][1]
        self.gap = self.trace[-1][2]
        self.answer = self.final_place if self.task_type == "place" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, place=self.place, speed=self.speed, accel=self.accel)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, place=place, gap=gap)
            for index, (speed, place, gap) in enumerate(self.trace, 1)
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
