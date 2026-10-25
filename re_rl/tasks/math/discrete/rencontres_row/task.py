"""RencontresRowTask — перестановки с данным числом неподвижных точек.

Субфакториал !0 = 1, !1 = 0, дальше !(n) = (n-1)*(!(n-1)+!(n-2)).
Число перестановок с k неподвижными точками равно C(n, k)*!(n-k).
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def subfactorials(order: int) -> List[int]:
    values = [1, 0]
    for index in range(2, order + 1):
        values.append((index - 1) * (values[-1] + values[-2]))
    return values[: order + 1]


def rencontres_row(order: int) -> List[int]:
    quiet = subfactorials(order)
    row = [math.comb(order, k) * quiet[order - k] for k in range(order + 1)]
    assert sum(row) == math.factorial(order)
    assert quiet[order] == int(sp.subfactorial(order))
    return row


class RencontresRowTask(BaseMathTask):
    TASK_TYPE = "rencontres_row"
    TASK_TYPES = ["fixed", "total"]

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
        self.quiet = subfactorials(self.n)
        self.row = rencontres_row(self.n)
        self.k = random.randint(0, self.n)
        self.fixed = self.row[self.k]
        self.total = sum(self.row)
        self.answer = self.fixed if self.task_type == "fixed" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "fixed" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.quiet)
        ]
        for k, value in enumerate(self.row):
            steps.append(texts.t(
                "s3", self.language, n=self.n, k=k,
                choose=math.comb(self.n, k), quiet=self.quiet[self.n - k], value=value,
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
