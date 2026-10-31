"""FloydDistanceTask — суммы и диаметр кратчайших путей по алгоритму Флойда.

Ориентированный граф сильно связен: есть цикл через все вершины и дополнительные дуги.
Считаются расстояния между различными упорядоченными парами. Номера вершин с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Edge = Tuple[int, int, int]


def floyd(n: int, edges: Sequence[Edge]) -> List[List[Optional[int]]]:
    dist: List[List[Optional[int]]] = [[0 if i == j else None for j in range(n)] for i in range(n)]
    for src, dst, weight in edges:
        if src == dst:
            continue
        if dist[src][dst] is None or weight < dist[src][dst]:
            dist[src][dst] = weight
    for mid in range(n):
        for src in range(n):
            for dst in range(n):
                if dist[src][mid] is None or dist[mid][dst] is None:
                    continue
                candidate = dist[src][mid] + dist[mid][dst]
                if dist[src][dst] is None or candidate < dist[src][dst]:
                    dist[src][dst] = candidate
    return dist


def floyd_stats(n: int, edges: Sequence[Edge]) -> Tuple[int, int]:
    dist = floyd(n, edges)
    total = 0
    diameter = 0
    for src in range(n):
        for dst in range(n):
            if src == dst:
                continue
            if dist[src][dst] is None:
                raise RuntimeError(texts.literal('literals.s4'))
            total += dist[src][dst]
            if dist[src][dst] > diameter:
                diameter = dist[src][dst]
    return total, diameter


from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import floyd_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace


class FloydDistanceTask(_GraphBase):
    TASK_TYPE = "floyd_distance"
    TASK_TYPES = ["sum", "diameter"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "extra": 1, "w": 4}, 2: {"n": 3, "extra": 2, "w": 5},
        3: {"n": 4, "extra": 2, "w": 5}, 4: {"n": 4, "extra": 3, "w": 6},
        5: {"n": 4, "extra": 4, "w": 6}, 6: {"n": 5, "extra": 4, "w": 7},
        7: {"n": 5, "extra": 5, "w": 8}, 8: {"n": 5, "extra": 6, "w": 8},
        9: {"n": 6, "extra": 6, "w": 9}, 10: {"n": 6, "extra": 8, "w": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.w = int(p["w"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.edges = [
            (i, (i + 1) % self.n, random.randint(1, self.w)) for i in range(self.n)
        ]
        for _ in range(self.extra):
            src = random.randrange(self.n)
            dst = random.randrange(self.n)
            if src != dst:
                self.edges.append((src, dst, random.randint(1, self.w)))
        self.total, self.diameter = floyd_stats(self.n, self.edges)
        self.answer = self.total if self.task_type == "sum" else self.diameter
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return ", ".join(f"{src + 1}->{dst + 1}: {weight}" for src, dst, weight in self.edges)

    def _descr(self, language):
        data = ((texts.t('s0', language, n=self.n, v1=self._shown())))
        if self.task_type == "sum":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{data} {ask}"

    def solve(self):
        self.total, self.diameter, self.algorithm_trace = floyd_trace(self.n, self.edges)
        self.answer = self.total if self.task_type == 'sum' else self.diameter
        self.solution_steps = render_trace(self.algorithm_trace, 'floyd', self.language, vertex_offset=1)
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
