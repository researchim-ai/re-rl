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

class TopologicalSortTask(_GraphBase):
    TASK_TYPE = "topological_sort"
    TASK_TYPES = ["order", "has_cycle"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 7},
        6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10}, 9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        n = self.n
        self.edges: List[Tuple[int, int]] = []
        if self.subtype == "has_cycle":
            self.has_cycle = random.random() < 0.5
        else:
            self.has_cycle = False
        order = list(range(n))
        random.shuffle(order)
        pos = {v: i for i, v in enumerate(order)}
        for _ in range(n + n // 2):
            a, b = random.sample(range(n), 2)
            if pos[a] < pos[b]:  # рёбра «вперёд» по порядку -> DAG
                if (a, b) not in self.edges:
                    self.edges.append((a, b))
        if self.subtype == "has_cycle" and self.has_cycle:
            if not self.edges:
                # без рёбер цикл невозможен — гарантируем хотя бы одно ребро
                a, b = random.sample(range(n), 2)
                self.edges.append((a, b))
            # добавляем обратное ребро, создающее цикл
            fwd = random.choice(self.edges)
            self.edges.append((fwd[1], fwd[0]))
        self._cycle = self._detect_cycle()

    def _detect_cycle(self):
        adj = defaultdict(list)
        indeg = defaultdict(int)
        nodes = set(range(self.n))
        for a, b in self.edges:
            adj[a].append(b); indeg[b] += 1
        q = deque([v for v in nodes if indeg[v] == 0])
        seen = 0
        while q:
            v = q.popleft(); seen += 1
            for w in adj[v]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    q.append(w)
        return seen != len(nodes)

    def _edges_str(self):
        return ", ".join(f"{a}→{b}" for a, b in self.edges)

    def _descr(self, language):
        head = ((texts.t('s0', language, v0=self.n - 1, v1=self._edges_str())))
        if self.subtype == "has_cycle":
            q = ((texts.t('s1', language)))
        else:
            q = ((texts.t('s2', language)))
        return head + q

    def solve(self):
        if self.subtype == "has_cycle":
            self.solution_steps = [
                ((texts.t('s5', self.language))),
                ((texts.t('s6', self.language) if self._cycle else
                   texts.t('s7', self.language))),
            ]
            self.final_answer = (texts.t('s3', self.language) if self._cycle else texts.t('s4', self.language))
        else:
            order = self._topo_order()
            self.solution_steps = [
                ((texts.t('s8', self.language))),
                ((texts.t('s9', self.language, v0=', '.join(map(str, order))))),
            ]
            self.final_answer = " ".join(map(str, order))

    def _topo_order(self):
        adj = defaultdict(list); indeg = defaultdict(int)
        for a, b in self.edges:
            adj[a].append(b); indeg[b] += 1
        q = deque(sorted(v for v in range(self.n) if indeg[v] == 0))
        order = []
        while q:
            v = q.popleft(); order.append(v)
            for w in adj[v]:
                indeg[w] -= 1
                if indeg[w] == 0:
                    q.append(w)
        return order

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "has_cycle":
            return U.verify_bool(prediction, bool(self._cycle))
        ints = U.parse_ints(prediction)
        if len(ints) < self.n:
            return 0.0
        order = ints[-self.n:]
        if sorted(order) != list(range(self.n)):
            return 0.0
        pos = {v: i for i, v in enumerate(order)}
        return 1.0 if all(pos[a] < pos[b] for a, b in self.edges) else 0.0
