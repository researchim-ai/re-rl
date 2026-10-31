"""Графовые алгоритмы как задачи с пошаговым решением.

Каждый класс — отдельный тип задачи с детерминированным алгоритмом-эталоном:
- WeightedShortestPathTask (Дейкстра),
- TopologicalSortTask (топосортировка / поиск цикла),
- GraphColoringTask (хроматическое число / k-раскрашиваемость),
- MSTWeightTask (вес остовного дерева, Крускал),
- EulerianPathTask (существование эйлерова пути),
- HamiltonianPathTask (существование гамильтонова пути),
- BipartiteMatchingTask (максимальное паросочетание, Кун),
- TSPTask (кратчайший гамильтонов цикл, перебор),
- MaxFlowTask (максимальный поток, Эдмондс–Карп),
- DAGLongestPathTask (длиннейший путь в DAG, ДП).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import heapq
import random
from collections import defaultdict, deque
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import dijkstra_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace

class WeightedShortestPathTask(_GraphBase):
    TASK_TYPE = texts.literal('literals.s3')
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "wmax": 6}, 2: {"n": 5, "wmax": 8}, 3: {"n": 5, "wmax": 9},
        4: {"n": 6, "wmax": 9}, 5: {"n": 7, "wmax": 9}, 6: {"n": 8, "wmax": 12},
        7: {"n": 9, "wmax": 15}, 8: {"n": 10, "wmax": 15}, 9: {"n": 11, "wmax": 20},
        10: {"n": 12, "wmax": 20},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.wmax = int(p["n"]), int(p["wmax"])
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        n = self.n
        self.edges: List[Tuple[int, int, int]] = []
        adj = defaultdict(list)
        perm = list(range(n))
        random.shuffle(perm)
        for i in range(1, n):  # остовное дерево — связность
            a, b = perm[i], perm[random.randrange(i)]
            w = random.randint(1, self.wmax)
            self.edges.append((a, b, w)); adj[a].append((b, w)); adj[b].append((a, w))
        seen = {tuple(sorted((a, b))) for a, b, _ in self.edges}
        for _ in range(n):
            a, b = random.sample(range(n), 2)
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            w = random.randint(1, self.wmax)
            self.edges.append((a, b, w)); adj[a].append((b, w)); adj[b].append((a, w))
        self.adj = adj
        self.src, self.dst = random.sample(range(n), 2)
        self._answer = self._dijkstra()

    def _dijkstra(self):
        dist = {self.src: 0}
        pq = [(0, self.src)]
        while pq:
            d, v = heapq.heappop(pq)
            if d > dist.get(v, 1e18):
                continue
            for w, wt in self.adj[v]:
                nd = d + wt
                if nd < dist.get(w, 1e18):
                    dist[w] = nd
                    heapq.heappush(pq, (nd, w))
        return dist.get(self.dst, -1)

    def _edges_str(self, language):
        return ", ".join(texts.t('s4', language, a=a, b=b, w=w) for a, b, w in self.edges)

    def _descr(self, language):
        return ((texts.t('s0', language, v0=self.n - 1, v1=self._edges_str(language), src=self.src, dst=self.dst)))

    def solve(self):
        self._answer, self.algorithm_trace = dijkstra_trace(self.n, self.edges, self.src, self.dst)
        self.shortest_path = self.algorithm_trace[-1]['path']
        self.solution_steps = render_trace(self.algorithm_trace, 'dijkstra', self.language)
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
