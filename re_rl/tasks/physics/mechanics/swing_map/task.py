"""SwingMapTask — дискретный маятник на целых числах.

Скорость теряет целую долю угла, затем угол получает скорость. Деление вниз считает SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def swing_trace(angle: int, rate: int, stiff: int, ticks: int) -> List[Tuple[int, int]]:
    theta = sp.Integer(angle)
    omega = sp.Integer(rate)
    stiffness = sp.Integer(stiff)
    trace = []
    for _ in range(ticks):
        omega -= theta // stiffness
        theta += omega
        trace.append((int(theta), int(omega)))
    return trace


class SwingMapTask(BaseMathTask):
    TASK_TYPE = "swing_map"
    TASK_TYPES = ["angle", "rate"]
    STIFF = 2

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
        self.angle = random.randint(1, 8)
        self.rate = random.randint(-2, 2)
        self.trace = swing_trace(self.angle, self.rate, self.STIFF, self.n)
        self.final_angle = self.trace[-1][0]
        self.final_rate = self.trace[-1][1]
        self.answer = self.final_angle if self.task_type == "angle" else self.final_rate
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "angle" else "s1"
        return texts.t(
            key, language, n=self.n, angle=self.angle, rate=self.rate, stiff=self.STIFF,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, angle=angle, rate=rate)
            for index, (angle, rate) in enumerate(self.trace, 1)
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
