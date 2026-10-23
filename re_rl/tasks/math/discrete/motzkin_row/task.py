"""MotzkinRowTask — числа Моцкина по двучленной рекурсии.

M(0) = 1, M(1) = 1. Дальше числитель (2*n+1)*M(n-1) + (3*n-3)*M(n-2) делится на n+2.
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def motzkin_trace(order: int) -> List[Tuple[int, int, int]]:
    values = [1, 1]
    trace = [(1, 1, 1), (1, 1, 1)]
    for n in range(2, order + 1):
        numer = (2 * n + 1) * values[-1] + (3 * n - 3) * values[-2]
        den = n + 2
        value = numer // den
        assert numer == value * den
        values.append(value)
        trace.append((numer, den, value))
    return trace[: order + 1]


class MotzkinRowTask(BaseMathTask):
    TASK_TYPE = "motzkin_row"
    TASK_TYPES = ["value", "numer"]

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
        self.trace = motzkin_trace(self.n)
        self.numer, self.den, self.value = self.trace[-1]
        assert self.value == int(sp.motzkin(self.n + 1))
        self.answer = self.value if self.task_type == "value" else self.numer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = []
        for index, (numer, den, value) in enumerate(self.trace):
            if index < 2:
                steps.append(texts.t("s2", self.language, n=index, value=value))
            else:
                steps.append(texts.t(
                    "s3", self.language, n=index, numer=numer, den=den, value=value,
                ))
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
