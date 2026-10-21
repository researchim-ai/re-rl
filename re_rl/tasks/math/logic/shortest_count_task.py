"""ShortestCountTask — кратчайшие пути в невзвешенном графе.

Подтипы:
- ``path_count`` — сколько кратчайших путей между двумя вершинами;
- ``level_size`` — сколько вершин лежит на заданном расстоянии от источника.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def bfs_ways(n: int, adj: List[List[int]], source: int):
    dist = [-1] * (n + 1)
    ways = [0] * (n + 1)
    dist[source] = 0
    ways[source] = 1
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                ways[v] = ways[u]
                queue.append(v)
            elif dist[v] == dist[u] + 1:
                ways[v] += ways[u]
    return dist, ways


class ShortestCountTask(BaseMathTask):
    TASK_TYPE = "shortest_path_count"
    TASK_TYPES = ["path_count", "level_size"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 1}, 2: {"n": 5, "extra": 1}, 3: {"n": 5, "extra": 2},
        4: {"n": 6, "extra": 2}, 5: {"n": 7, "extra": 2}, 6: {"n": 8, "extra": 3},
        7: {"n": 8, "extra": 3}, 8: {"n": 9, "extra": 4}, 9: {"n": 10, "extra": 4},
        10: {"n": 12, "extra": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        edges = set()
        for v in range(2, self.n + 1):
            edges.add((random.randint(1, v - 1), v))
        while len(edges) < self.n - 1 + self.extra:
            a, b = random.sample(range(1, self.n + 1), 2)
            edges.add((min(a, b), max(a, b)))
        self.edges = sorted(edges)
        self.adj = [[] for _ in range(self.n + 1)]
        for a, b in self.edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self.source = 1
        self.dist, self.ways = bfs_ways(self.n, self.adj, self.source)
        reachable = [v for v in range(1, self.n + 1) if self.dist[v] > 0]
        self.target = random.choice(reachable)
        self.k = random.randint(0, max(self.dist))
        self.path_count = self.ways[self.target]
        self.level = sum(1 for v in range(1, self.n + 1) if self.dist[v] == self.k)
        self.answer = self.path_count if self.task_type == "path_count" else self.level

    def _edge_text(self) -> str:
        return ", ".join(f"{a}-{b}" for a, b in self.edges)

    def _descr(self, language):
        ru = language == "ru"
        head = ((f"Невзвешенный неориентированный граф, вершины 1..{self.n}, рёбра: {self._edge_text()}.")
                if ru else
                (f"Unweighted undirected graph, vertices 1..{self.n}, edges: {self._edge_text()}."))
        if self.task_type == "path_count":
            ask = ((f"Сколько различных кратчайших путей между {self.source} и {self.target}?") if ru else
                   (f"How many distinct shortest paths are there between {self.source} and {self.target}?"))
        else:
            ask = ((f"Сколько вершин находится на расстоянии {self.k} от вершины {self.source}?") if ru else
                   (f"How many vertices are at distance {self.k} from vertex {self.source}?"))
        return f"{head} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "path_count":
            step = ((f"BFS: расстояние {self.dist[self.target]}, число путей {self.path_count}.") if ru else
                    (f"BFS: distance {self.dist[self.target]}, number of paths {self.path_count}."))
        else:
            step = ((f"На расстоянии {self.k} лежит {self.level} вершин.") if ru else
                    (f"{self.level} vertices lie at distance {self.k}."))
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
