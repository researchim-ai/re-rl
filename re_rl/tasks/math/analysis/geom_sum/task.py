"""GeomSumTask — сумма геометрической прогрессии.

Каждый член — предыдущий, умноженный на знаменатель. Первый член равен 1.
Число членов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def geom_trace(ratio: int, count: int) -> List[Tuple[int, int]]:
    power = 1
    total = 0
    trace = []
    for _ in range(count):
        total += power
        trace.append((power, total))
        power *= ratio
    return trace


def geom_closed(ratio: int, count: int) -> int:
    index = sp.symbols("i")
    value = sp.summation(ratio ** index, (index, 0, count - 1))
    return int(value)


class GeomSumTask(BaseMathTask):
    TASK_TYPE = "geom_sum"
    TASK_TYPES = ["total", "last"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "r": 2}, 2: {"n": 3, "r": 2}, 3: {"n": 4, "r": 2},
        4: {"n": 5, "r": 2}, 5: {"n": 6, "r": 3}, 6: {"n": 7, "r": 2},
        7: {"n": 8, "r": 3}, 8: {"n": 9, "r": 2}, 9: {"n": 10, "r": 2},
        10: {"n": 12, "r": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.ratio = max(2, int(p["r"]))
        self.trace = geom_trace(self.ratio, self.n)
        self.last, self.total = self.trace[-1]
        assert self.total == geom_closed(self.ratio, self.n)
        self.answer = self.total if self.task_type == "total" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, ratio=self.ratio)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, power=power, total=total)
            for index, (power, total) in enumerate(self.trace, 1)
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
