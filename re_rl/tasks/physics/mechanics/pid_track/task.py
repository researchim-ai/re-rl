"""PidTrackTask — дискретный регулятор положения по ошибке, сумме и приращению.

Сила складывается из трёх целых частей, а место сдвигается на целую половину силы.
Сложение считает SymPy. Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pid_trace(target: int, place: int, ticks: int) -> List[Tuple[int, int]]:
    spot = sp.Integer(place)
    goal = sp.Integer(target)
    memory = sp.Integer(0)
    previous = sp.Integer(0)
    trace = []
    for _ in range(ticks):
        error = goal - spot
        memory += error
        slope = error - previous
        force = error + memory + slope
        spot += force // 2
        previous = error
        trace.append((int(spot), int(memory)))
    return trace


class PidTrackTask(BaseMathTask):
    TASK_TYPE = "pid_track"
    TASK_TYPES = ["place", "memory"]

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
        self.target = random.randint(1, 8)
        self.start = random.randint(0, 6)
        self.trace = pid_trace(self.target, self.start, self.n)
        self.spot = self.trace[-1][0]
        self.memory = self.trace[-1][1]
        self.answer = self.spot if self.task_type == "place" else self.memory
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, target=self.target, start=self.start)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, place=place, memory=memory)
            for index, (place, memory) in enumerate(self.trace, 1)
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
