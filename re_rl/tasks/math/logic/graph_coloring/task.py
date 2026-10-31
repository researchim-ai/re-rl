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
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import coloring_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace

class GraphColoringTask(_GraphBase):
    TASK_TYPE = "graph_coloring"
    TASK_TYPES = ["chromatic", "k_colorable"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 8}, 10: {"n": 9},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.subtype = subtype or kwargs.get("task_type") or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        n = self.n
        self.edges = []
        for a in range(n):
            for b in range(a + 1, n):
                if random.random() < 0.4:
                    self.edges.append((a, b))
        self.chromatic = self._chromatic_number()
        if self.subtype == "k_colorable":
            self.k = random.randint(max(1, self.chromatic - 1), self.chromatic + 1)
            self._answer_bool = self.k >= self.chromatic

    def _k_colorable(self, k):
        adj = defaultdict(set)
        for a, b in self.edges:
            adj[a].add(b); adj[b].add(a)
        color = [0] * self.n

        def bt(v):
            if v == self.n:
                return True
            for c in range(1, k + 1):
                if all(color[u] != c for u in adj[v] if u < v):
                    color[v] = c
                    if bt(v + 1):
                        return True
                    color[v] = 0
            return False

        return bt(0)

    def _chromatic_number(self):
        for k in range(1, self.n + 1):
            if self._k_colorable(k):
                return k
        return self.n

    def _edges_str(self):
        return ", ".join(f"({a}-{b})" for a, b in self.edges) or texts.t('s9', self.language)

    def _descr(self, language):
        head = ((texts.t('s0', language, v0=self.n - 1, v1=self._edges_str())))
        if self.subtype == "chromatic":
            q = ((texts.t('s1', language)))
        else:
            q = ((texts.t('s2', language, k=self.k)))
        return head + q

    def solve(self):
        limit = self.k if self.subtype == 'k_colorable' else None
        chromatic, self.algorithm_trace = coloring_trace(self.n, self.edges, limit)
        self.solution_steps = render_trace(self.algorithm_trace, 'color', self.language)
        if self.subtype == 'chromatic':
            self.chromatic = chromatic
            self.final_answer = str(chromatic)
        else:
            self._answer_bool = chromatic is not None
            self.final_answer = texts.t('s3', self.language) if self._answer_bool else texts.t('s4', self.language)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "chromatic":
            return U.verify_int(prediction, int(self.chromatic))
        return U.verify_bool(prediction, bool(self._answer_bool))
