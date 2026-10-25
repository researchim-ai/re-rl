"""RocketBurnTask — разгон ракеты целыми порциями топлива.

За такт к скорости прибавляется частное скорости истечения и текущей массы, затем масса уменьшается на 1.
Частные считает SymPy. Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def burn_trace(mass: int, exhaust: int, ticks: int) -> List[Tuple[int, int]]:
    left = sp.Integer(mass)
    speed = sp.Integer(0)
    push = sp.Integer(exhaust)
    trace = []
    for _ in range(ticks):
        speed += push // left
        left -= 1
        trace.append((int(speed), int(left)))
    return trace


class RocketBurnTask(BaseMathTask):
    TASK_TYPE = "rocket_burn"
    TASK_TYPES = ["speed", "mass"]

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
        self.mass = self.n + random.randint(2, 8)
        self.exhaust = random.randint(6, 24)
        self.trace = burn_trace(self.mass, self.exhaust, self.n)
        self.speed = self.trace[-1][0]
        self.final_mass = self.trace[-1][1]
        self.answer = self.speed if self.task_type == "speed" else self.final_mass
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "speed" else "s1"
        return texts.t(key, language, n=self.n, mass=self.mass, exhaust=self.exhaust)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, mass=mass)
            for index, (speed, mass) in enumerate(self.trace, 1)
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
