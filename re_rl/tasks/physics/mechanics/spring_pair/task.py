"""SpringPairTask — две массы, соединённые пружиной единичной жёсткости.

Сила линейна по растяжению. Шаг переводит состояние матрицей SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_UPDATE = sp.Matrix([
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [-1, 1, 1, 0],
    [1, -1, 0, 1],
])


def spring_trace(left: int, right: int, speed_left: int, speed_right: int,
                 rest: int, ticks: int) -> List[Tuple[int, int]]:
    state = sp.Matrix([left, right, speed_left, speed_right])
    shift = sp.Matrix([-rest, rest, -rest, rest])
    trace = []
    for _ in range(ticks):
        state = _UPDATE * state + shift
        gap = int(state[1] - state[0])
        speed = int(state[2])
        trace.append((gap, speed))
    return trace


class SpringPairTask(BaseMathTask):
    TASK_TYPE = "spring_pair"
    TASK_TYPES = ["gap", "speed"]

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
        self.left = 0
        self.right = random.randint(1, 6)
        self.speed_left = random.randint(-2, 2)
        self.speed_right = random.randint(-2, 2)
        self.rest = random.randint(1, 4)
        self.trace = spring_trace(
            self.left, self.right, self.speed_left, self.speed_right, self.rest, self.n,
        )
        self.gap = self.trace[-1][0]
        self.final_speed = self.trace[-1][1]
        self.answer = self.gap if self.task_type == "gap" else self.final_speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "gap" else "s1"
        return texts.t(
            key, language, n=self.n, left=self.left, right=self.right,
            speed_left=self.speed_left, speed_right=self.speed_right, rest=self.rest,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gap=gap, speed=speed)
            for index, (gap, speed) in enumerate(self.trace, 1)
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
