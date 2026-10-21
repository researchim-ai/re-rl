"""FloydDistanceTask — суммы и диаметр кратчайших путей по алгоритму Флойда.

Ориентированный граф сильно связен: есть цикл через все вершины и дополнительные дуги.
Считаются расстояния между различными упорядоченными парами. Номера вершин с 1.
"""

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
                raise RuntimeError("граф не сильно связен")
            total += dist[src][dst]
            if dist[src][dst] > diameter:
                diameter = dist[src][dst]
    return total, diameter


class FloydDistanceTask(BaseMathTask):
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
        ru = language == "ru"
        data = ((f"Ориентированный граф из {self.n} вершин, номера с 1. Дуги: {self._shown()}. "
                 f"Если дуга повторяется, остаётся меньший вес.") if ru else
                (f"Directed graph with {self.n} vertices, numbered from 1. Arcs: {self._shown()}. "
                 f"If an arc is repeated, the smaller weight remains."))
        if self.task_type == "sum":
            ask = (("Найдите сумму длин кратчайших путей по всем упорядоченным парам различных вершин.")
                   if ru else
                   ("Find the sum of shortest-path lengths over all ordered pairs of distinct vertices."))
        else:
            ask = (("Найдите диаметр: наибольшую длину кратчайшего пути между различными вершинами.")
                   if ru else
                   ("Find the diameter: the greatest shortest-path length between distinct vertices."))
        return f"{data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Сумма расстояний {self.total}, диаметр {self.diameter}.") if ru else
                (f"Distance sum {self.total}, diameter {self.diameter}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
