"""NarayanaRowTask — числа Нараяны одной строки.

N(n, k) = C(n, k)*C(n, k-1)/n для k от 1 до n. Деление целое. Сумма строки — число Каталана.
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def narayana_trace(order: int) -> List[Tuple[int, int, int]]:
    row = []
    for k in range(1, order + 1):
        left = binom(order, k)
        right = binom(order, k - 1)
        numer = left * right
        assert numer % order == 0
        row.append((left, right, numer // order))
    assert sum(item[2] for item in row) == int(sp.catalan(order))
    return row


class NarayanaRowTask(BaseMathTask):
    TASK_TYPE = "narayana_row"
    TASK_TYPES = ["entry", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = narayana_trace(self.n)
        self.k = random.randint(1, self.n)
        self.entry = self.trace[self.k - 1][2]
        self.total = sum(item[2] for item in self.trace)
        self.answer = self.entry if self.task_type == "entry" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, n=self.n, k=index, km1=index - 1,
                left=left, right=right, value=value,
            )
            for index, (left, right, value) in enumerate(self.trace, 1)
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
