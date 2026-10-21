"""TriangleGirthTask — локальная структура неориентированного графа.

Подтипы:
- ``triangles`` — число треугольников (троек попарно смежных вершин);
- ``girth``     — длина кратчайшего цикла, 0 если циклов нет.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def count_triangles(n: int, edges: List[Tuple[int, int]]) -> int:
    adj = [set() for _ in range(n + 1)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    total = 0
    for a, b in edges:
        total += len(adj[a] & adj[b])
    return total // 3


def graph_girth(n: int, edges: List[Tuple[int, int]]) -> int:
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    best: Optional[int] = None
    for start in range(1, n + 1):
        dist = [-1] * (n + 1)
        parent = [-1] * (n + 1)
        dist[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif v != parent[u]:
                    length = dist[u] + dist[v] + 1
                    if best is None or length < best:
                        best = length
    return 0 if best is None else best


class TriangleGirthTask(BaseMathTask):
    TASK_TYPE = "triangle_girth"
    TASK_TYPES = ["triangles", "girth"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 1}, 2: {"n": 5, "extra": 2}, 3: {"n": 5, "extra": 3},
        4: {"n": 6, "extra": 3}, 5: {"n": 6, "extra": 4}, 6: {"n": 7, "extra": 4},
        7: {"n": 8, "extra": 5}, 8: {"n": 8, "extra": 6}, 9: {"n": 9, "extra": 6},
        10: {"n": 10, "extra": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        edges = set()
        for v in range(2, self.n + 1):
            edges.add((random.randint(1, v - 1), v))
        target = self.n - 1 + self.extra
        while len(edges) < target:
            a, b = random.sample(range(1, self.n + 1), 2)
            edges.add((min(a, b), max(a, b)))
        self.edges = sorted((min(a, b), max(a, b)) for a, b in edges)
        self.triangles = count_triangles(self.n, self.edges)
        self.girth = graph_girth(self.n, self.edges)
        self.answer = self.triangles if self.task_type == "triangles" else self.girth
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{a}-{b}" for a, b in self.edges)
        head = ((texts.t('s0', language, n=self.n, shown=shown)))
        if self.task_type == "triangles":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{head} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, triangles=self.triangles, girth=self.girth)))
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
