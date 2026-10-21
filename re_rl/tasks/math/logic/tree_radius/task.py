"""TreeRadiusTask — радиус и эксцентриситет дерева.

Эксцентриситет вершины — расстояние до самой дальней вершины.
Радиус — минимальный эксцентриситет.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def distances(n: int, adj: List[List[int]], source: int) -> List[int]:
    dist = [-1] * (n + 1)
    dist[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def eccentricities(n: int, edges: List[Tuple[int, int]]) -> List[int]:
    adj = [[] for _ in range(n + 1)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    ecc = [0] * (n + 1)
    for v in range(1, n + 1):
        ecc[v] = max(distances(n, adj, v)[1:])
    return ecc


class TreeRadiusTask(BaseMathTask):
    TASK_TYPE = "tree_radius"
    TASK_TYPES = ["radius", "eccentricity"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 7},
        6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10}, 9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        edges = [(random.randint(1, v - 1), v) for v in range(2, self.n + 1)]
        self.edges = sorted((min(a, b), max(a, b)) for a, b in edges)
        self.ecc = eccentricities(self.n, self.edges)
        self.radius = min(self.ecc[1:])
        self.vertex = random.randint(1, self.n)
        self.answer = self.radius if self.task_type == "radius" else self.ecc[self.vertex]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{a}-{b}" for a, b in self.edges)
        head = ((texts.t('s0', language, n=self.n, shown=shown)))
        if self.task_type == "radius":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language, vertex=self.vertex)))
        return f"{head} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, radius=self.radius, vertex=self.vertex, v2=self.ecc[self.vertex])))
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
