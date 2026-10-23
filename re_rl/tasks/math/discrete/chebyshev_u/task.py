"""ChebyshevUTask — многочлены Чебышёва второго рода в целой точке.

U0 = 1, U1 = 2*x, дальше U = 2*x*предыдущий минус предпредыдущий.
Степень растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def chebyshev_u_trace(degree: int, point: int) -> List[int]:
    values = [1, 2 * point]
    for _ in range(1, degree):
        values.append(2 * point * values[-1] - values[-2])
    return values[: degree + 1]


class ChebyshevUTask(BaseMathTask):
    TASK_TYPE = "chebyshev_u"
    TASK_TYPES = ["value", "total"]

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
        self.point = random.randint(0, 3)
        self.trace = chebyshev_u_trace(self.n, self.point)
        self.value = self.trace[-1]
        self.total = sum(self.trace)
        assert self.value == int(sp.chebyshevu(self.n, self.point))
        self.answer = self.value if self.task_type == "value" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        twice = 2 * self.point
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, point=self.point, twice=twice)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.trace)
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
