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

class TSPTask(_GraphBase):
    TASK_TYPE = "tsp"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "wmax": 9}, 2: {"n": 4, "wmax": 12}, 3: {"n": 5, "wmax": 12},
        4: {"n": 5, "wmax": 15}, 5: {"n": 6, "wmax": 15}, 6: {"n": 6, "wmax": 20},
        7: {"n": 7, "wmax": 20}, 8: {"n": 7, "wmax": 25}, 9: {"n": 8, "wmax": 25},
        10: {"n": 8, "wmax": 30},
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
        self.d = [[0] * n for _ in range(n)]
        for a in range(n):
            for b in range(a + 1, n):
                w = random.randint(1, self.wmax)
                self.d[a][b] = self.d[b][a] = w
        self._answer = self._best_tour()

    def _best_tour(self):
        n = self.n
        best = None
        for perm in permutations(range(1, n)):
            route = (0,) + perm
            cost = sum(self.d[route[i]][route[(i + 1) % n]] for i in range(n))
            if best is None or cost < best:
                best = cost
        return best

    def _descr(self, language):
        lines = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                lines.append(f"{a}-{b}: {self.d[a][b]}")
        table = "; ".join(lines)
        return ((texts.t('s0', language, n=self.n, v1=self.n - 1, table=table)))

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
