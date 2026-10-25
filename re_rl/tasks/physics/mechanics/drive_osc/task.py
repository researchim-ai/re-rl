"""DriveOscTask — осциллятор с внешним толчком на каждом такте.

Скорость получает толчок минус координату, затем координата получает новую скорость.
Шаг сверяют символьно через матрицу SymPy. Число толчков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def drive_trace(place: int, speed: int, drives: Sequence[int]) -> List[Tuple[int, int]]:
    update = sp.Matrix([[0, 1], [-1, 1]])
    state = sp.Matrix([place, speed])
    spot = sp.Integer(place)
    velocity = sp.Integer(speed)
    trace = []
    for drive in drives:
        kick = sp.Integer(drive)
        state = update * state + sp.Matrix([kick, kick])
        velocity = velocity + kick - spot
        spot = spot + velocity
        if state[0] != spot or state[1] != velocity:
            raise RuntimeError("state mismatch")
        trace.append((int(spot), int(velocity)))
    return trace


class DriveOscTask(BaseMathTask):
    TASK_TYPE = "drive_osc"
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
        self.start = random.randint(-2, 3)
        self.speed = random.randint(-2, 3)
        self.drives = [random.randint(-2, 3) for _ in range(self.n)]
        self.trace = drive_trace(self.start, self.speed, self.drives)
        self.place = self.trace[-1][0]
        self.final_speed = self.trace[-1][1]
        self.answer = self.place if self.task_type == "place" else self.final_speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, place=self.start, speed=self.speed,
                       drives=self._row(self.drives))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, place=place, speed=speed)
            for index, (place, speed) in enumerate(self.trace, 1)
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
