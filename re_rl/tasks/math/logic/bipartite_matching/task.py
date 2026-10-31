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
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import matching_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace

class BipartiteMatchingTask(_GraphBase):
    TASK_TYPE = "bipartite_matching"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 2, "R": 2}, 2: {"L": 3, "R": 3}, 3: {"L": 3, "R": 3}, 4: {"L": 4, "R": 4},
        5: {"L": 4, "R": 4}, 6: {"L": 5, "R": 5}, 7: {"L": 5, "R": 5}, 8: {"L": 6, "R": 6},
        9: {"L": 6, "R": 6}, 10: {"L": 7, "R": 7},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L, self.R = int(p["L"]), int(p["R"])
        self.augment = augment
        self._build()
        self._finish(self._descr(language), language, detail_level, output_format, reasoning_mode)

    def _build(self):
        self.pairs = []
        self.adj = defaultdict(list)
        for l in range(self.L):
            for r in range(self.R):
                if random.random() < 0.45:
                    self.pairs.append((l, r)); self.adj[l].append(r)
        self._answer = self._max_matching()

    def _max_matching(self):
        match_r = {}

        def try_kuhn(l, visited):
            for r in self.adj[l]:
                if r not in visited:
                    visited.add(r)
                    if r not in match_r or try_kuhn(match_r[r], visited):
                        match_r[r] = l
                        return True
            return False

        result = 0
        for l in range(self.L):
            if try_kuhn(l, set()):
                result += 1
        return result

    def _descr(self, language):
        es = ", ".join(f"(L{l}-R{r})" for l, r in self.pairs) or ((texts.t('s1', language)))
        return ((texts.t('s0', language, v0=self.L - 1, v1=self.R - 1, es=es)))

    def solve(self):
        self._answer, self.algorithm_trace = matching_trace(self.L, self.R, self.pairs)
        self.solution_steps = render_trace(self.algorithm_trace, 'matching', self.language)
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
