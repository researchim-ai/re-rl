"""WienerTask — индекс Винера связного неориентированного графа.

Это сумма расстояний по всем неупорядоченным парам вершин.
Граф строится от дерева, поэтому он связен.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.structural_traces import wiener_trace
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
            raise RuntimeError(texts.literal('literals.s2'))
        total += sum(dist[1:])
    return total // 2


class WienerTask(_GraphBase):
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
        shown = ", ".join(f"{a}-{b}" for a, b in self.edges)
        return ((texts.t('s0', language, n=self.n, shown=shown)))

    def solve(self):
        self.answer, self.algorithm_trace = wiener_trace(self.n, self.edges)
        self.solution_steps = render_trace(self.algorithm_trace, 'wiener', self.language)
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
