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
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import kruskal_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace

class MSTWeightTask(_GraphBase):
    TASK_TYPE = "mst_weight"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "wmax": 9}, 2: {"n": 5, "wmax": 9}, 3: {"n": 5, "wmax": 12},
        4: {"n": 6, "wmax": 12}, 5: {"n": 7, "wmax": 15}, 6: {"n": 8, "wmax": 15},
        7: {"n": 9, "wmax": 20}, 8: {"n": 10, "wmax": 20}, 9: {"n": 11, "wmax": 25},
        10: {"n": 12, "wmax": 30},
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
        self.edges = []
        seen = set()
        perm = list(range(n)); random.shuffle(perm)
        for i in range(1, n):
            a, b = perm[i], perm[random.randrange(i)]
            key = (min(a, b), max(a, b))
            seen.add(key)
            self.edges.append((a, b, random.randint(1, self.wmax)))
        for _ in range(n):
            a, b = random.sample(range(n), 2)
            key = (min(a, b), max(a, b))
            if key not in seen:
                seen.add(key)
                self.edges.append((a, b, random.randint(1, self.wmax)))
        self._answer = self._kruskal()

    def _kruskal(self):
        parent = list(range(self.n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        total = 0
        for a, b, w in sorted(self.edges, key=lambda e: e[2]):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                total += w
        return total

    def _descr(self, language):
        es = ", ".join(texts.t('s3', language, a=a, b=b, w=w) for a, b, w in self.edges)
        return ((texts.t('s0', language, v0=self.n - 1, es=es)))

    def solve(self):
        self._answer, self.algorithm_trace = kruskal_trace(self.n, self.edges)
        self.solution_steps = render_trace(self.algorithm_trace, 'kruskal', self.language)
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
