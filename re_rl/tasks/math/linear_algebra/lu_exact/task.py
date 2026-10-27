"""LuExactTask — целочисленное LU-разложение без перестановок.

Множитель строки делится нацело на опорный элемент, а определитель равен произведению опорных.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Sequence[int]


def _det(rows: Sequence[Row]) -> int:
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
        raise RuntimeError("factor mismatch")
    return int(value)


def lu_trace(rows: Sequence[Row]) -> List[Tuple[int, int]]:
    width = len(rows)
    if width < 2 or any(len(row) != width for row in rows):
        raise RuntimeError("factor mismatch")
    grid = [list(row) for row in rows]
    product = 1
    total = 0
    trace = []
    for col in range(width):
        pivot = grid[col][col]
        if pivot == 0:
            raise RuntimeError("factor mismatch")
        product *= pivot
        for row in range(col + 1, width):
            if grid[row][col] % pivot != 0:
                raise RuntimeError("factor mismatch")
            factor = grid[row][col] // pivot
            total += factor
            for index in range(col, width):
                grid[row][index] -= factor * grid[col][index]
            if grid[row][col] != 0:
                raise RuntimeError("factor mismatch")
        trace.append((pivot, total))
    if product != _det(rows):
        raise RuntimeError("factor mismatch")
    return trace


class LuExactTask(BaseMathTask):
    TASK_TYPE = "lu_exact"
    TASK_TYPES = ["det", "mult"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        lower = [[0] * self.n for _ in range(self.n)]
        upper = [[0] * self.n for _ in range(self.n)]
        for row in range(self.n):
            lower[row][row] = 1
            upper[row][row] = random.choice((-2, -1, 1, 2))
            for col in range(row):
                lower[row][col] = random.choice((-2, -1, 1, 2)) if row == col + 1 else random.randint(-1, 1)
            for col in range(row + 1, self.n):
                upper[row][col] = random.randint(-2, 2)
        self.rows = []
        for row in range(self.n):
            line = []
            for col in range(self.n):
                total = 0
                for mid in range(min(row, col) + 1):
                    total += lower[row][mid] * upper[mid][col]
                line.append(total)
            self.rows.append(line)
        self.trace = lu_trace(self.rows)
        self.det = 1
        for pivot, _total in self.trace:
            self.det *= pivot
        self.mult = self.trace[-1][1]
        self.answer = self.det if self.task_type == "det" else self.mult
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(" ".join(str(value) for value in row) for row in self.rows)

    def _descr(self, language):
        key = "s0" if self.task_type == "det" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pivot=pivot, mult=mult)
            for index, (pivot, mult) in enumerate(self.trace, 1)
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
