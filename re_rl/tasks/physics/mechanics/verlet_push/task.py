"""VerletPushTask — скоростной Верле с чётным ускорением.

Половина ускорения добавляется до сдвига и половина после. Половины считает SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def verlet_trace(place: int, speed: int, accels: Sequence[int]) -> List[Tuple[int, int]]:
    coord = sp.Integer(place)
    velocity = sp.Integer(speed)
    trace = []
    for accel in accels:
        half = sp.Rational(int(accel), 2)
        velocity += half
        coord += velocity
        velocity += half
        trace.append((int(coord), int(velocity)))
    return trace


class VerletPushTask(BaseMathTask):
    TASK_TYPE = "verlet_push"
    TASK_TYPES = ["place", "speed"]

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
        self.place = random.randint(0, 3)
        self.speed = random.randint(-2, 2)
        self.accels = [random.choice([-4, -2, 2, 4]) for _ in range(self.n)]
        self.trace = verlet_trace(self.place, self.speed, self.accels)
        self.final_place = self.trace[-1][0]
        self.final_speed = self.trace[-1][1]
        self.answer = self.final_place if self.task_type == "place" else self.final_speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(accel) for accel in self.accels)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, place=self.place, speed=self.speed, accels=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, accel=accel, place=place, speed=speed)
            for index, (accel, (place, speed)) in enumerate(zip(self.accels, self.trace), 1)
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
