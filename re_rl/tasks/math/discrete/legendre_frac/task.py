"""LegendreFracTask — числитель многочлена Лежандра.

P0 = 1, P1 = x. Дальше (n+1)*P следующего = (2*n+1)*x*P текущий минус n*P предыдущий.
Степень растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def reduce_frac(numer: int, denom: int) -> Tuple[int, int]:
    if denom < 0:
        numer, denom = -numer, -denom
    common = math.gcd(numer, denom)
    return numer // common, denom // common


def legendre_trace(degree: int, point: int) -> List[Tuple[int, int]]:
    values = [(1, 1), (point, 1)]
    for n in range(1, degree):
        left_n, left_d = values[-1]
        prev_n, prev_d = values[-2]
        numer = (2 * n + 1) * point * left_n * prev_d - n * prev_n * left_d
        denom = left_d * prev_d * (n + 1)
        values.append(reduce_frac(numer, denom))
    return values[: degree + 1]


class LegendreFracTask(BaseMathTask):
    TASK_TYPE = "legendre_frac"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.point = random.choice((2, 3))
        self.trace = legendre_trace(self.n, self.point)
        self.numer, self.denom = self.trace[-1]
        library = sp.legendre(self.n, self.point).as_numer_denom()
        assert (self.numer, self.denom) == (int(library[0]), int(library[1]))
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, point=self.point)

    def solve(self):
        steps = [
            texts.t("s2", self.language, n=0, numer=self.trace[0][0], denom=self.trace[0][1]),
            texts.t("s2", self.language, n=1, numer=self.trace[1][0], denom=self.trace[1][1]),
        ]
        for n in range(1, self.n):
            numer, denom = self.trace[n + 1]
            steps.append(texts.t(
                "s3", self.language, n=n, degree=n + 1, numer=numer, denom=denom,
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
