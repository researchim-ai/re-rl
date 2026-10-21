"""TopoCountTask — число топологических порядков небольшого DAG.

Рёбра идут от меньшего номера к большему. Считаются маски: если все
предшественники уже взяты, вершину можно поставить следующей.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def count_topological_orders(n: int, edges: List[Tuple[int, int]]) -> int:
    pred = [[] for _ in range(n)]
    for u, v in edges:
        pred[v].append(u)
    total = 1 << n
    dp = [0] * total
    dp[0] = 1
    for mask in range(total):
        if dp[mask] == 0:
            continue
        for vertex in range(n):
            if mask & (1 << vertex):
                continue
            if all(mask & (1 << parent) for parent in pred[vertex]):
                dp[mask | (1 << vertex)] += dp[mask]
    return dp[total - 1]


class TopoCountTask(BaseMathTask):
    TASK_TYPE = "topo_count"
    TASK_TYPES = ["orders"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "p": 0.2}, 2: {"n": 3, "p": 0.4}, 3: {"n": 4, "p": 0.25},
        4: {"n": 4, "p": 0.4}, 5: {"n": 5, "p": 0.25}, 6: {"n": 5, "p": 0.35},
        7: {"n": 6, "p": 0.25}, 8: {"n": 6, "p": 0.35}, 9: {"n": 7, "p": 0.2},
        10: {"n": 8, "p": 0.18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.prob = float(p["p"])
        self.task_type = "orders"
        self.augment = augment
        edges = set()
        for u in range(self.n):
            for v in range(u + 1, self.n):
                if random.random() < self.prob:
                    edges.add((u, v))
        self.edges = sorted(edges)
        self.answer = count_topological_orders(self.n, self.edges)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(f"{u + 1}->{v + 1}" for u, v in self.edges) or "-"
        return ((f"Ориентированный ациклический граф, вершины 1..{self.n}, рёбра: {shown}. "
                 f"Ребро a->b означает, что a стоит раньше b. Сколько существует топологических порядков?")
                if ru else
                (f"A directed acyclic graph, vertices 1..{self.n}, edges: {shown}. "
                 f"Edge a->b means a comes before b. How many topological orders are there?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Перебор допустимых масок даёт {self.answer} порядков.") if ru else
             (f"Enumeration of feasible masks gives {self.answer} orders.")),
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
