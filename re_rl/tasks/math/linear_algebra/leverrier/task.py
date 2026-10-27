"""LeverrierTask — коэффициенты характеристического многочлена методом Леверье.

На шаге k след новой матрицы делится нацело на k, а в конце матрица плюс свободный член на диагонали равна нулю.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Grid = Tuple[Tuple[int, ...], ...]
State = Tuple[int, Grid]


def _det(rows: Sequence[Sequence[int]]) -> int:
    width = len(rows)
    grid = [[Fraction(value) for value in row] for row in rows]
    sign = 1
    for col in range(width):
        pivot = next((row for row in range(col, width) if grid[row][col] != 0), None)
        if pivot is None:
            return 0
        if pivot != col:
            grid[col], grid[pivot] = grid[pivot], grid[col]
            sign = -sign
        scale = grid[col][col]
        for row in range(col + 1, width):
            factor = grid[row][col] / scale
            if factor == 0:
                continue
            for index in range(col, width):
                grid[row][index] -= factor * grid[col][index]
    value = Fraction(sign)
    for col in range(width):
        value *= grid[col][col]
    if value.denominator != 1:
        raise RuntimeError("char mismatch")
    return int(value)


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(row) for row in rows)


def lever_trace(rows: Sequence[Sequence[int]]) -> List[State]:
    width = len(rows)
    if width < 1 or any(len(row) != width for row in rows):
        raise RuntimeError("char mismatch")
    base = _freeze(rows)
    work = [list(row) for row in base]
    coef = -sum(work[i][i] for i in range(width))
    trace = [(coef, _freeze(work))]
    for step in range(2, width + 1):
        shifted = [list(row) for row in work]
        for index in range(width):
            shifted[index][index] += coef
        work = [[0] * width for _ in range(width)]
        for row in range(width):
            for col in range(width):
                work[row][col] = sum(base[row][mid] * shifted[mid][col] for mid in range(width))
        diag = sum(work[index][index] for index in range(width))
        if diag % step != 0:
            raise RuntimeError("char mismatch")
        coef = (-diag) // step
        trace.append((coef, _freeze(work)))
    for row in range(width):
        for col in range(width):
            extra = coef if row == col else 0
            if work[row][col] + extra != 0:
                raise RuntimeError("char mismatch")
    signed = _det(base) if width % 2 == 0 else -_det(base)
    if coef != signed:
        raise RuntimeError("char mismatch")
    if width >= 2:
        pairs = 0
        for left in range(width):
            for right in range(left + 1, width):
                pairs += base[left][left] * base[right][right] - base[left][right] * base[right][left]
        if trace[1][0] != pairs:
            raise RuntimeError("char mismatch")
    return trace


class LeverrierTask(BaseMathTask):
    TASK_TYPE = "leverrier"
    TASK_TYPES = ["const", "pair"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 5}, 8: {"n": 6},
        9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rows = [
            [random.randint(-1, 1) for _ in range(self.n)] for _ in range(self.n)
        ]
        self.trace = lever_trace(self.rows)
        self.const = self.trace[-1][0]
        self.pair = self.trace[1][0]
        self.answer = self.const if self.task_type == "const" else self.pair
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(" ".join(str(value) for value in row) for row in self.rows)

    def _grid(self, rows: Grid) -> str:
        return "; ".join(" ".join(str(value) for value in row) for row in rows)

    def _descr(self, language):
        key = "s0" if self.task_type == "const" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, coef=coef, grid=self._grid(grid))
            for index, (coef, grid) in enumerate(self.trace, 1)
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
