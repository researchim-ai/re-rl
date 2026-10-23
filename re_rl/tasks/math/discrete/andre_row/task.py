"""AndreRowTask — числа Андре по треугольнику Энтрингера.

Строка 0 равна 1. Клетка k строки n — это предыдущая клетка строки плюс клетка n-k предыдущей строки.
Число Андре — последняя клетка строки. Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def andre_rows(order: int) -> List[List[int]]:
    rows = [[1]]
    for n in range(1, order + 1):
        previous = rows[-1]
        row = []
        for k in range(n + 1):
            left = row[-1] if k else 0
            index = n - k
            above = previous[index] if 0 <= index < len(previous) else 0
            row.append(left + above)
        rows.append(row)
    return rows


class AndreRowTask(BaseMathTask):
    TASK_TYPE = "andre_row"
    TASK_TYPES = ["value", "cell"]

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
        self.rows = andre_rows(self.n)
        self.k = random.randint(0, self.n)
        self.value = self.rows[-1][-1]
        self.cell = self.rows[-1][self.k]
        assert self.value == int(sp.andre(self.n))
        self.answer = self.value if self.task_type == "value" else self.cell
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = []
        for n, row in enumerate(self.rows):
            for k, value in enumerate(row):
                if n == 0:
                    left, above = 0, value
                else:
                    left = 0 if k == 0 else row[k - 1]
                    index = n - k
                    previous = self.rows[n - 1]
                    above = previous[index] if 0 <= index < len(previous) else 0
                steps.append(texts.t(
                    "s2", self.language, n=n, k=k, left=left, above=above, value=value,
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
