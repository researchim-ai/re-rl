"""WienerTask — индекс Винера связного неориентированного графа.

Это сумма расстояний по всем неупорядоченным парам вершин.
Граф строится от дерева, поэтому он связен.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def wiener_index(n: int, edges: List[Tuple[int, int]]) -> int:
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    total = 0
    for source in range(1, n + 1):
        dist = [-1] * (n + 1)
        dist[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        if any(dist[v] < 0 for v in range(1, n + 1)):
            raise RuntimeError("граф для индекса Винера несвязен")
        total += sum(dist[1:])
    return total // 2


class WienerTask(BaseMathTask):
    TASK_TYPE = "wiener_index"
    TASK_TYPES = ["sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 0}, 2: {"n": 4, "extra": 1}, 3: {"n": 5, "extra": 1},
        4: {"n": 5, "extra": 1}, 5: {"n": 6, "extra": 2}, 6: {"n": 7, "extra": 2},
        7: {"n": 8, "extra": 2}, 8: {"n": 9, "extra": 3}, 9: {"n": 10, "extra": 3},
        10: {"n": 12, "extra": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = "sum"
        self.augment = augment
        edges = set()
        for v in range(2, self.n + 1):
            edges.add((random.randint(1, v - 1), v))
        while len(edges) < self.n - 1 + self.extra:
            a, b = random.sample(range(1, self.n + 1), 2)
            edges.add((min(a, b), max(a, b)))
        self.edges = sorted(edges)
        self.answer = wiener_index(self.n, self.edges)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(f"{a}-{b}" for a, b in self.edges)
        return ((f"Связный неориентированный граф, вершины 1..{self.n}, рёбра: {shown}. "
                 f"Найдите индекс Винера: сумму расстояний по всем неупорядоченным парам вершин.")
                if ru else
                (f"A connected undirected graph, vertices 1..{self.n}, edges: {shown}. "
                 f"Find the Wiener index: the sum of distances over all unordered pairs of vertices."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Сумма попарных расстояний равна {self.answer}.") if ru else
             (f"The sum of pairwise distances is {self.answer}.")),
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
