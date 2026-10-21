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

class DAGLongestPathTask(_GraphBase):
    TASK_TYPE = texts.literal('literals.s3')
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "wmax": 6}, 2: {"n": 5, "wmax": 8}, 3: {"n": 5, "wmax": 9},
        4: {"n": 6, "wmax": 9}, 5: {"n": 7, "wmax": 12}, 6: {"n": 8, "wmax": 12},
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
        order = list(range(n)); random.shuffle(order)
        pos = {v: i for i, v in enumerate(order)}
        self.edges = []
        seen = set()
        for _ in range(2 * n):
            a, b = random.sample(range(n), 2)
            if pos[a] < pos[b] and (a, b) not in seen:
                seen.add((a, b))
                self.edges.append((a, b, random.randint(1, self.wmax)))
        self._order = order
        self._answer = self._longest()

    def _longest(self):
        adj = defaultdict(list)
        for a, b, w in self.edges:
            adj[a].append((b, w))
        best = {v: 0 for v in range(self.n)}
        for v in reversed(self._order):
            for b, w in adj[v]:
                best[v] = max(best[v], w + best[b])
        return max(best.values()) if best else 0

    def _descr(self, language):
        es = ", ".join(texts.t('s4', language, a=a, b=b, w=w) for a, b, w in self.edges)
        return ((texts.t('s0', language, v0=self.n - 1, es=es)))

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
