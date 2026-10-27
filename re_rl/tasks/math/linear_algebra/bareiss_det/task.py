"""BareissDetTask — определитель алгоритмом Барейса.

Нижний блок пересчитывается минором два на два и делится нацело на предыдущий ведущий минор.
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
        raise RuntimeError("bareiss mismatch")
    return int(value)


def bareiss_trace(rows: Sequence[Row]) -> List[Tuple[int, int]]:
    width = len(rows)
    if width < 2 or any(len(row) != width for row in rows):
        raise RuntimeError("bareiss mismatch")
    grid = [list(row) for row in rows]
    previous = 1
    trace = []
    for col in range(width - 1):
        pivot = grid[col][col]
        if pivot == 0:
            raise RuntimeError("bareiss mismatch")
        for row in range(col + 1, width):
            for index in range(col + 1, width):
                numer = pivot * grid[row][index] - grid[row][col] * grid[col][index]
                if numer % previous != 0:
                    raise RuntimeError("bareiss mismatch")
                grid[row][index] = numer // previous
        trace.append((pivot, grid[width - 1][width - 1]))
        previous = pivot
    if trace[-1][1] != _det(rows):
        raise RuntimeError("bareiss mismatch")
    return trace


class BareissDetTask(BaseMathTask):
    TASK_TYPE = "bareiss_det"
    TASK_TYPES = ["det", "minor"]

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
        self.rows = []
        for row in range(self.n):
            line = [random.randint(-2, 2) for _ in range(self.n)]
            line[row] = 0
            line[row] = sum(abs(value) for value in line) + random.randint(1, 3)
            self.rows.append(line)
        self.trace = bareiss_trace(self.rows)
        self.minor = self.trace[-1][0]
        self.det = self.trace[-1][1]
        self.answer = self.det if self.task_type == "det" else self.minor
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
            texts.t("s2", self.language, i=index, pivot=pivot, corner=corner)
            for index, (pivot, corner) in enumerate(self.trace, 1)
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
