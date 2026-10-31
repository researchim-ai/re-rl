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
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import hamilton_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace

class HamiltonianPathTask(_GraphBase):
    TASK_TYPE = "hamiltonian_path"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 8}, 10: {"n": 9},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        n = self.n
        self.edges = []
        for a in range(n):
            for b in range(a + 1, n):
                if random.random() < 0.45:
                    self.edges.append((a, b))
        self._answer = self._has_hamiltonian()

    def _has_hamiltonian(self):
        adj = defaultdict(set)
        for a, b in self.edges:
            adj[a].add(b); adj[b].add(a)
        n = self.n
        # ДП по битовым маскам: dp[mask][v] — можно ли покрыть mask, закончив в v.
        dp = [[False] * n for _ in range(1 << n)]
        for v in range(n):
            dp[1 << v][v] = True
        for mask in range(1 << n):
            for v in range(n):
                if not dp[mask][v]:
                    continue
                for w in adj[v]:
                    if not (mask >> w) & 1:
                        dp[mask | (1 << w)][w] = True
        full = (1 << n) - 1
        return any(dp[full][v] for v in range(n))

    def _descr(self, language):
        es = ", ".join(f"({a}-{b})" for a, b in self.edges) or ((texts.t('s3', language)))
        return ((texts.t('s0', language, v0=self.n - 1, es=es)))

    def solve(self):
        self._answer, self.algorithm_trace = hamilton_trace(self.n, self.edges)
        self.solution_steps = render_trace(self.algorithm_trace, 'hamilton', self.language)
        self.final_answer = texts.t('s1', self.language) if self._answer else texts.t('s2', self.language)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
