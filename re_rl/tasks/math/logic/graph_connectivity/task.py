"""GraphConnectivityTask — связность и структура графов.

Подтипы:
- ``scc``                — число компонент сильной связности (орграф);
- ``articulation_points``— число точек сочленения (неориентированный связный граф);
- ``bridges``            — число мостов (неориентированный связный граф);
- ``negative_cycle``     — есть ли отрицательный цикл (взвешенный орграф, да/нет).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import sys
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GraphConnectivityTask(BaseMathTask):
    TASK_TYPE = "graph_connectivity"
    TASK_TYPES = ["scc", "articulation_points", "bridges", "negative_cycle"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 2}, 2: {"n": 5, "extra": 2}, 3: {"n": 5, "extra": 3},
        4: {"n": 6, "extra": 3}, 5: {"n": 7, "extra": 4}, 6: {"n": 8, "extra": 4},
        7: {"n": 9, "extra": 5}, 8: {"n": 10, "extra": 6}, 9: {"n": 11, "extra": 7},
        10: {"n": 12, "extra": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # --- генерация ---
    def _random_tree_edges(self) -> List[Tuple[int, int]]:
        edges = []
        for v in range(1, self.n):
            u = random.randrange(v)
            edges.append((u, v))
        return edges

    def _build(self):
        if self.task_type == "scc":
            self.directed = True
            edges = set()
            m = self.n + self.extra
            while len(edges) < m:
                a, b = random.randrange(self.n), random.randrange(self.n)
                if a != b:
                    edges.add((a, b))
            self.edges = sorted(edges)
            self.answer = self._count_scc()
        elif self.task_type in ("articulation_points", "bridges"):
            self.directed = False
            edges = set(self._random_tree_edges())  # связный остов
            while len(edges) < self.n - 1 + self.extra:
                a, b = random.randrange(self.n), random.randrange(self.n)
                if a != b:
                    edges.add((min(a, b), max(a, b)))
            self.edges = sorted(edges)
            aps, brs = self._articulation_and_bridges()
            self.answer = len(aps) if self.task_type == "articulation_points" else len(brs)
        else:  # negative_cycle
            self.directed = True
            edges = {}
            m = self.n + self.extra
            while len(edges) < m:
                a, b = random.randrange(self.n), random.randrange(self.n)
                if a != b and (a, b) not in edges:
                    edges[(a, b)] = random.randint(-5, 8)
            self.wedges = [(a, b, w) for (a, b), w in sorted(edges.items())]
            self.answer = self._has_negative_cycle()

    # --- алгоритмы ---
    def _count_scc(self) -> int:
        adj = [[] for _ in range(self.n)]
        radj = [[] for _ in range(self.n)]
        for a, b in self.edges:
            adj[a].append(b)
            radj[b].append(a)
        visited = [False] * self.n
        order = []

        def dfs1(s):
            stack = [(s, 0)]
            visited[s] = True
            while stack:
                v, i = stack.pop()
                if i < len(adj[v]):
                    stack.append((v, i + 1))
                    w = adj[v][i]
                    if not visited[w]:
                        visited[w] = True
                        stack.append((w, 0))
                else:
                    order.append(v)

        for v in range(self.n):
            if not visited[v]:
                dfs1(v)
        comp = [-1] * self.n
        c = 0
        for v in reversed(order):
            if comp[v] == -1:
                stack = [v]
                comp[v] = c
                while stack:
                    x = stack.pop()
                    for w in radj[x]:
                        if comp[w] == -1:
                            comp[w] = c
                            stack.append(w)
                c += 1
        return c

    def _articulation_and_bridges(self):
        adj = [set() for _ in range(self.n)]
        for a, b in self.edges:
            adj[a].add(b)
            adj[b].add(a)
        disc = [-1] * self.n
        low = [0] * self.n
        aps = set()
        bridges = []
        timer = [0]
        sys.setrecursionlimit(10000)

        def dfs(u, parent):
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            children = 0
            for w in adj[u]:
                if w == parent:
                    continue
                if disc[w] == -1:
                    children += 1
                    dfs(w, u)
                    low[u] = min(low[u], low[w])
                    if low[w] > disc[u]:
                        bridges.append((min(u, w), max(u, w)))
                    if parent != -1 and low[w] >= disc[u]:
                        aps.add(u)
                else:
                    low[u] = min(low[u], disc[w])
            if parent == -1 and children > 1:
                aps.add(u)

        for v in range(self.n):
            if disc[v] == -1:
                dfs(v, -1)
        return aps, bridges

    def _has_negative_cycle(self) -> bool:
        dist = [0] * self.n  # виртуальный исток с 0-рёбрами ко всем вершинам
        for _ in range(self.n):
            changed = False
            for a, b, w in self.wedges:
                if dist[a] + w < dist[b]:
                    dist[b] = dist[a] + w
                    changed = True
            if not changed:
                return False
        for a, b, w in self.wedges:
            if dist[a] + w < dist[b]:
                return True
        return False

    # --- описание/решение ---
    def _edges_str(self):
        if self.task_type == "negative_cycle":
            return ", ".join(f"{a}→{b}({w})" for a, b, w in self.wedges)
        arrow = "→" if self.directed else "—"
        return ", ".join(f"{a}{arrow}{b}" for a, b in self.edges)

    def _descr(self, language):
        head_v = f"0..{self.n-1}"
        if self.task_type == "scc":
            return ((texts.t('s1', language, head_v=head_v, v1=self._edges_str())))
        if self.task_type == "articulation_points":
            return ((texts.t('s2', language, head_v=head_v, v1=self._edges_str())))
        if self.task_type == "bridges":
            return ((texts.t('s3', language, head_v=head_v, v1=self._edges_str())))
        return ((texts.t('s0', language, head_v=head_v, v1=self._edges_str())))

    def solve(self):
        steps = {
            "scc": ((texts.t('s6', self.language))),
            "articulation_points": ((texts.t('s7', self.language))),
            "bridges": ((texts.literal('literals.s8'))),
            "negative_cycle": ((texts.t('s9', self.language))),
        }[self.task_type]
        if self.task_type == "negative_cycle":
            ans = (texts.t('s4', self.language) if self.answer else texts.t('s5', self.language))
        else:
            ans = str(self.answer)
        self.final_answer = ans
        self.solution_steps = [steps, ((texts.common('answer_line', self.language, answer=ans)))]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "negative_cycle":
            return U.verify_bool(prediction, bool(self.answer))
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3,
                             difficulty=5, reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
