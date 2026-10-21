"""DagPathsTask — число путей из 1 в n в ориентированном ациклическом графе.

Рёбра идут только от меньшего номера к большему, поэтому порядок 1..n топологический.
Динамика: ways[v] = сумма ways[u] по рёбрам u->v, ways[1] = 1.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def count_paths(n: int, edges: List[Tuple[int, int]]) -> int:
    incoming = [[] for _ in range(n + 1)]
    for u, v in edges:
        incoming[v].append(u)
    ways = [0] * (n + 1)
    ways[1] = 1
    for v in range(2, n + 1):
        ways[v] = sum(ways[u] for u in incoming[v])
    return ways[n]


class DagPathsTask(BaseMathTask):
    TASK_TYPE = "dag_paths"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "p": 0.3}, 2: {"n": 4, "p": 0.4}, 3: {"n": 5, "p": 0.35},
        4: {"n": 5, "p": 0.45}, 5: {"n": 6, "p": 0.35}, 6: {"n": 6, "p": 0.45},
        7: {"n": 7, "p": 0.3}, 8: {"n": 8, "p": 0.28}, 9: {"n": 8, "p": 0.35},
        10: {"n": 9, "p": 0.25},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.prob = float(p["p"])
        self.task_type = "count"
        self.augment = augment
        edges = set()
        if random.random() < 0.8:
            for i in range(1, self.n):
                edges.add((i, i + 1))
        for u in range(1, self.n):
            for v in range(u + 1, self.n + 1):
                if random.random() < self.prob:
                    edges.add((u, v))
        self.edges = sorted(edges)
        self.answer = count_paths(self.n, self.edges)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(f"{u}->{v}" for u, v in self.edges) or "-"
        return ((f"Ориентированный граф на вершинах 1..{self.n}, рёбра только вперёд: {shown}. "
                 f"Сколько различных путей из 1 в {self.n}?") if ru else
                (f"A directed graph on vertices 1..{self.n}, edges only forward: {shown}. "
                 f"How many distinct paths go from 1 to {self.n}?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Динамика по топологическому порядку даёт {self.answer} путей.") if ru else
             (f"DP in topological order gives {self.answer} paths.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
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
