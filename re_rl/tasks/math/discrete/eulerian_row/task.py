"""EulerianRowTask — эйлеровы числа перестановок.

A(1, 0) = 1. Дальше A(n, k) = (k+1)*A(n-1, k) + (n-k)*A(n-1, k-1).
Сумма строки равна n!. Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def eulerian_rows(order: int) -> List[List[int]]:
    rows = [[1]]
    for n in range(2, order + 1):
        previous = rows[-1]
        row = []
        for k in range(n):
            same = previous[k] if k < len(previous) else 0
            left = previous[k - 1] if k else 0
            row.append((k + 1) * same + (n - k) * left)
        rows.append(row)
    return rows


class EulerianRowTask(BaseMathTask):
    TASK_TYPE = "eulerian_row"
    TASK_TYPES = ["entry", "total"]

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
        self.rows = eulerian_rows(self.n)
        self.k = random.randint(0, self.n - 1)
        self.entry = self.rows[-1][self.k]
        self.total = sum(self.rows[-1])
        assert self.total == math.factorial(self.n)
        self.answer = self.entry if self.task_type == "entry" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [texts.t("s3", self.language)]
        for n, row in enumerate(self.rows[1:], 2):
            previous = self.rows[n - 2]
            for k, value in enumerate(row):
                same = previous[k] if k < len(previous) else 0
                left = previous[k - 1] if k and previous else 0
                steps.append(texts.t(
                    "s2", self.language, n=n, k=k, same=same, left=left,
                    factor=k + 1, other=n - k, value=value,
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
