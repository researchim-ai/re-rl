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

class EulerianPathTask(_GraphBase):
    TASK_TYPE = "eulerian_path"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 7}, 9: {"n": 8}, 10: {"n": 8},
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
        seen = set()
        perm = list(range(n)); random.shuffle(perm)
        for i in range(1, n):  # связность
            a, b = perm[i], perm[random.randrange(i)]
            key = (min(a, b), max(a, b)); seen.add(key)
            self.edges.append((a, b))
        for _ in range(random.randint(0, n)):
            a, b = random.sample(range(n), 2)
            key = (min(a, b), max(a, b))
            if key not in seen:
                seen.add(key); self.edges.append((a, b))
        self._answer = self._has_eulerian()

    def _has_eulerian(self):
        deg = defaultdict(int)
        adj = defaultdict(set)
        for a, b in self.edges:
            deg[a] += 1; deg[b] += 1; adj[a].add(b); adj[b].add(a)
        nonzero = [v for v in range(self.n) if deg[v] > 0]
        if not nonzero:
            return False
        seen = {nonzero[0]}; stack = [nonzero[0]]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in seen:
                    seen.add(w); stack.append(w)
        if any(v not in seen for v in nonzero):
            return False
        odd = sum(1 for v in nonzero if deg[v] % 2 == 1)
        return odd in (0, 2)

    def _descr(self, language):
        es = ", ".join(f"({a}-{b})" for a, b in self.edges)
        return ((texts.t('s0', language, v0=self.n - 1, es=es)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language) if self._answer else
               texts.t('s5', self.language))),
        ]
        self.final_answer = (texts.t('s1', self.language) if self._answer else texts.t('s2', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
