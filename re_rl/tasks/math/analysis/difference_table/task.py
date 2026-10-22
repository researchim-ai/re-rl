"""DifferenceTableTask — следующее значение многочлена по конечным разностям.

Даны значения в точках 0, 1, ..., d. Степень равна d, поэтому старшая разность постоянна.
Число известных значений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    value = 1
    for index in range(1, k + 1):
        value = value * (n - k + index) // index
    return value


def polynomial_value(coeffs: List[int], point: int) -> int:
    return sum(coeff * binom(point, index) for index, coeff in enumerate(coeffs))


def extend_table(values: List[int]) -> int:
    rows = [values[:]]
    while len(rows[-1]) > 1:
        current = rows[-1]
        rows.append([current[index + 1] - current[index] for index in range(len(current) - 1)])
    rows[-1].append(rows[-1][-1])
    for level in range(len(rows) - 2, -1, -1):
        rows[level].append(rows[level][-1] + rows[level + 1][-1])
    return rows[0][-1]


class DifferenceTableTask(BaseMathTask):
    TASK_TYPE = "difference_table"
    TASK_TYPES = ["next", "delta"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 1, "c": 4}, 2: {"d": 1, "c": 5}, 3: {"d": 2, "c": 4},
        4: {"d": 2, "c": 5}, 5: {"d": 3, "c": 3}, 6: {"d": 4, "c": 3},
        7: {"d": 4, "c": 3}, 8: {"d": 5, "c": 2}, 9: {"d": 6, "c": 2},
        10: {"d": 7, "c": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.degree = max(1, int(p["d"]))
        self.n = self.degree + 1
        limit = int(p["c"])
        self.coeffs = [random.randint(-limit, limit) for _ in range(self.degree)]
        leading = random.randint(1, limit) * random.choice((-1, 1))
        self.coeffs.append(leading)
        self.values = [polynomial_value(self.coeffs, point) for point in range(self.n)]
        self.nxt = polynomial_value(self.coeffs, self.n)
        self.delta = leading
        self.answer = self.nxt if self.task_type == "next" else self.delta
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.values)
        key = "s0" if self.task_type == "next" else "s1"
        return texts.t(key, language, degree=self.degree, last=self.degree, listing=listing, point=self.n)

    def solve(self):
        steps = []
        row = self.values[:]
        level = 0
        while len(row) > 1:
            level += 1
            row = [row[index + 1] - row[index] for index in range(len(row) - 1)]
            shown = ", ".join(str(item) for item in row)
            steps.append(texts.t("s2", self.language, i=level, listing=shown))
        steps.append(texts.t("s3", self.language, delta=self.delta, nxt=self.nxt, point=self.n))
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
