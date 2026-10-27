"""NilLogTask — логарифм единичной плюс строго верхней треугольной матрицы.

Ряд обрывается, каждый член умножен на общий знаменатель, и знак чередуется.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Grid = Tuple[Tuple[int, ...], ...]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(row) for row in rows)


def _mul(left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]) -> List[List[int]]:
    width = len(left)
    return [
        [sum(left[row][mid] * right[mid][col] for mid in range(width)) for col in range(width)]
        for row in range(width)
    ]


def unilog_trace(rows: Sequence[Sequence[int]]) -> List[Grid]:
    width = len(rows)
    if width < 2 or any(len(row) != width for row in rows):
        raise RuntimeError("log mismatch")
    for row in range(width):
        for col in range(row + 1):
            if rows[row][col] != 0:
                raise RuntimeError("log mismatch")
    scale = 1
    for k in range(1, width):
        scale = scale // math.gcd(scale, k) * k
    power = [list(row) for row in rows]
    total = [[0] * width for _ in range(width)]
    trace = []
    for k in range(1, width):
        sign = 1 if k % 2 == 1 else -1
        coef = sign * (scale // k)
        for row in range(width):
            for col in range(width):
                total[row][col] += coef * power[row][col]
        trace.append(_freeze(total))
        power = _mul(power, rows)
    if any(value != 0 for line in power for value in line):
        raise RuntimeError("log mismatch")
    return trace


class NilLogTask(BaseMathTask):
    TASK_TYPE = "nil_log"
    TASK_TYPES = ["corner", "mass"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rows = []
        for row in range(self.n):
            self.rows.append([0] * (row + 1) + [random.randint(-1, 1) for _ in range(self.n - row - 1)])
        self.trace = unilog_trace(self.rows)
        self.corner = self.trace[-1][0][self.n - 1]
        self.mass = sum(sum(row) for row in self.trace[-1])
        self.answer = self.corner if self.task_type == "corner" else self.mass
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(" ".join(str(value) for value in row) for row in self.rows)

    def _grid(self, rows: Grid) -> str:
        return "; ".join(" ".join(str(value) for value in row) for row in rows)

    def _descr(self, language):
        key = "s0" if self.task_type == "corner" else "s1"
        return texts.t(key, language, n=self.n, last=self.n - 1, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, grid=self._grid(grid))
            for index, grid in enumerate(self.trace, 1)
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
