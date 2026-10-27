"""KronEntryTask — элемент и след кронекерова произведения.

Старший бит выбирает первый множитель, а след большого произведения равен произведению следов.
Число множителей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Factor = Tuple[Tuple[int, int], Tuple[int, int]]


def _kron(left: List[List[int]], right: Factor) -> List[List[int]]:
    rows = len(left)
    cols = len(left[0])
    out = [[0] * (cols * 2) for _ in range(rows * 2)]
    for i in range(rows):
        for j in range(cols):
            scale = left[i][j]
            for p in range(2):
                for q in range(2):
                    out[i * 2 + p][j * 2 + q] = scale * right[p][q]
    return out


def kron_trace(factors: Sequence[Factor], row: int, col: int) -> List[Tuple[int, int]]:
    count = len(factors)
    limit = 1 << count
    if count < 1 or not 0 <= row < limit or not 0 <= col < limit:
        raise RuntimeError("kron mismatch")
    entry = 1
    span = 1
    trace = []
    for index, factor in enumerate(factors):
        shift = count - 1 - index
        entry *= factor[(row >> shift) & 1][(col >> shift) & 1]
        span *= factor[0][0] + factor[1][1]
        trace.append((entry, span))
    mass = 1
    for factor in factors:
        mass *= factor[0][0] + factor[0][1] + factor[1][0] + factor[1][1]
    if count <= 5:
        grid = [[1]]
        for factor in factors:
            grid = _kron(grid, factor)
        if grid[row][col] != entry or sum(grid[i][i] for i in range(len(grid))) != span:
            raise RuntimeError("kron mismatch")
        total = sum(sum(line) for line in grid)
        if total != mass:
            raise RuntimeError("kron mismatch")
    return trace


class KronEntryTask(BaseMathTask):
    TASK_TYPE = "kron_entry"
    TASK_TYPES = ["entry", "span"]

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
        self.n = max(1, int(p["n"]))
        self.factors = []
        for _ in range(self.n):
            self.factors.append((
                (random.randint(-2, 2), random.randint(-2, 2)),
                (random.randint(-2, 2), random.randint(-2, 2)),
            ))
        self.row = random.randint(0, (1 << self.n) - 1)
        self.col = random.randint(0, (1 << self.n) - 1)
        self.trace = kron_trace(self.factors, self.row, self.col)
        self.entry = self.trace[-1][0]
        self.span = self.trace[-1][1]
        self.answer = self.entry if self.task_type == "entry" else self.span
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(
            f"{a} {b} {c} {d}" for (a, b), (c, d) in self.factors
        )

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, row=self.row, col=self.col, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, entry=entry, span=span)
            for index, (entry, span) in enumerate(self.trace, 1)
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
