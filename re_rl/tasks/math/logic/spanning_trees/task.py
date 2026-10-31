"""SpanningTreesTask — число остовных деревьев по матричной теореме Кирхгофа.

Берётся любой минор лапласиана. Определитель считается точно, через дроби,
и оказывается целым неотрицательным числом.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.structural_traces import spanning_trace
from re_rl.tasks.math.logic import _logic_utils as U


def integer_det(matrix: List[List[int]]) -> int:
    size = len(matrix)
    if size == 0:
        return 1
    data = [[Fraction(value) for value in row] for row in matrix]
    sign = 1
    for col in range(size):
        pivot = next((row for row in range(col, size) if data[row][col] != 0), None)
        if pivot is None:
            return 0
        if pivot != col:
            data[col], data[pivot] = data[pivot], data[col]
            sign = -sign
        scale = data[col][col]
        for row in range(col + 1, size):
            if data[row][col] == 0:
                continue
            factor = data[row][col] / scale
            for k in range(col, size):
                data[row][k] -= factor * data[col][k]
    result = Fraction(sign)
    for i in range(size):
        result *= data[i][i]
    if result.denominator != 1:
        raise RuntimeError(texts.literal('literals.s2'))
    return int(result)


def spanning_trees(n: int, edges: List[Tuple[int, int]]) -> int:
    lap = [[0] * n for _ in range(n)]
    for a, b in edges:
        lap[a][a] += 1
        lap[b][b] += 1
        lap[a][b] -= 1
        lap[b][a] -= 1
    minor = [row[:-1] for row in lap[:-1]]
    count = integer_det(minor)
    if count < 0:
        raise RuntimeError(texts.literal('literals.s3'))
    return count


class SpanningTreesTask(_GraphBase):
    TASK_TYPE = "spanning_trees"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "extra": 0}, 2: {"n": 3, "extra": 1}, 3: {"n": 4, "extra": 1},
        4: {"n": 4, "extra": 2}, 5: {"n": 5, "extra": 2}, 6: {"n": 5, "extra": 3},
        7: {"n": 6, "extra": 3}, 8: {"n": 6, "extra": 4}, 9: {"n": 7, "extra": 4},
        10: {"n": 7, "extra": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = "count"
        self.augment = augment
        edges = set()
        planted = random.random() < 0.85
        if planted:
            for v in range(1, self.n):
                edges.add((random.randrange(v), v))
        want = len(edges) + self.extra
        while len(edges) < want:
            a, b = random.sample(range(self.n), 2)
            edges.add((min(a, b), max(a, b)))
        self.edges = sorted(edges)
        self.answer = spanning_trees(self.n, self.edges)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{a + 1}-{b + 1}" for a, b in self.edges) or "-"
        return ((texts.t('s0', language, n=self.n, shown=shown)))

    def solve(self):
        self.answer, self.algorithm_trace = spanning_trace(self.n, self.edges)
        self.solution_steps = render_trace(self.algorithm_trace, 'spanning', self.language, vertex_offset=1)
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
