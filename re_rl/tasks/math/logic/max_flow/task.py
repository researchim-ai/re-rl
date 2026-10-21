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

class MaxFlowTask(_GraphBase):
    TASK_TYPE = "max_flow"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "cmax": 6}, 2: {"n": 4, "cmax": 9}, 3: {"n": 5, "cmax": 9},
        4: {"n": 5, "cmax": 12}, 5: {"n": 6, "cmax": 12}, 6: {"n": 6, "cmax": 15},
        7: {"n": 7, "cmax": 15}, 8: {"n": 7, "cmax": 20}, 9: {"n": 8, "cmax": 20},
        10: {"n": 8, "cmax": 25},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.cmax = int(p["n"]), int(p["cmax"])
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        n = self.n
        self.s, self.t = 0, n - 1
        self.cap_edges = []
        # Слоистая структура по порядку вершин, дуги «вперёд».
        for a in range(n):
            for b in range(a + 1, n):
                if random.random() < 0.5:
                    c = random.randint(1, self.cmax)
                    self.cap_edges.append((a, b, c))
        # гарантируем путь s->t
        for v in range(n - 1):
            if not any(e[0] == v and e[1] == v + 1 for e in self.cap_edges):
                self.cap_edges.append((v, v + 1, random.randint(1, self.cmax)))
        self._answer = self._edmonds_karp()

    def _edmonds_karp(self):
        n = self.n
        cap = [[0] * n for _ in range(n)]
        for a, b, c in self.cap_edges:
            cap[a][b] += c
        flow = 0
        while True:
            parent = [-1] * n
            parent[self.s] = self.s
            q = deque([self.s])
            while q:
                v = q.popleft()
                for w in range(n):
                    if parent[w] == -1 and cap[v][w] > 0:
                        parent[w] = v
                        q.append(w)
            if parent[self.t] == -1:
                break
            aug = 1 << 30
            v = self.t
            while v != self.s:
                aug = min(aug, cap[parent[v]][v]); v = parent[v]
            v = self.t
            while v != self.s:
                cap[parent[v]][v] -= aug
                cap[v][parent[v]] += aug
                v = parent[v]
            flow += aug
        return flow

    def _descr(self, language):
        es = ", ".join(f"{a}→{b} (c={c})" for a, b, c in self.cap_edges)
        return ((texts.t('s0', language, v0=self.n - 1, s=self.s, t=self.t, es=es)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
