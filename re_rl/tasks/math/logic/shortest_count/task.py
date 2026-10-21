"""ShortestCountTask — кратчайшие пути в невзвешенном графе.

Подтипы:
- ``path_count`` — сколько кратчайших путей между двумя вершинами;
- ``level_size`` — сколько вершин лежит на заданном расстоянии от источника.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
    TASK_TYPE = texts.literal('literals.s5')
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
        head = ((texts.t('s0', language, n=self.n, v1=self._edge_text())))
        if self.task_type == "path_count":
            ask = ((texts.t('s1', language, source=self.source, target=self.target)))
        else:
            ask = ((texts.t('s2', language, k=self.k, source=self.source)))
        return f"{head} {ask}"

    def solve(self):
        if self.task_type == "path_count":
            step = ((texts.t('s3', self.language, v0=self.dist[self.target], path_count=self.path_count)))
        else:
            step = ((texts.t('s4', self.language, k=self.k, level=self.level)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
