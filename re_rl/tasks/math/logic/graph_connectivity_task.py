"""GraphConnectivityTask — связность и структура графов.

Подтипы:
- ``scc``                — число компонент сильной связности (орграф);
- ``articulation_points``— число точек сочленения (неориентированный связный граф);
- ``bridges``            — число мостов (неориентированный связный граф);
- ``negative_cycle``     — есть ли отрицательный цикл (взвешенный орграф, да/нет).
"""

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
        ru = language == "ru"
        head_v = f"0..{self.n-1}"
        if self.task_type == "scc":
            return ((f"Ориентированный граф, вершины {head_v}. Дуги: {self._edges_str()}. Сколько в "
                     f"нём компонент сильной связности?") if ru else
                    (f"Directed graph, vertices {head_v}. Arcs: {self._edges_str()}. How many "
                     f"strongly connected components does it have?"))
        if self.task_type == "articulation_points":
            return ((f"Неориентированный связный граф, вершины {head_v}. Рёбра: {self._edges_str()}. "
                     f"Сколько в нём точек сочленения (вершин, удаление которых увеличивает число "
                     f"компонент)?") if ru else
                    (f"Undirected connected graph, vertices {head_v}. Edges: {self._edges_str()}. "
                     f"How many articulation points (cut vertices) does it have?"))
        if self.task_type == "bridges":
            return ((f"Неориентированный связный граф, вершины {head_v}. Рёбра: {self._edges_str()}. "
                     f"Сколько в нём мостов (рёбер, удаление которых увеличивает число компонент)?")
                    if ru else
                    (f"Undirected connected graph, vertices {head_v}. Edges: {self._edges_str()}. "
                     f"How many bridges does it have?"))
        return ((f"Взвешенный ориентированный граф, вершины {head_v}. Дуги (в скобках — вес): "
                 f"{self._edges_str()}. Есть ли в графе отрицательный цикл? Ответьте да/нет.") if ru else
                (f"Weighted directed graph, vertices {head_v}. Arcs (weight in parentheses): "
                 f"{self._edges_str()}. Does the graph contain a negative cycle? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        steps = {
            "scc": ("Конденсация по Косараджу: два обхода в глубину." if ru else
                    "Kosaraju's condensation: two DFS passes."),
            "articulation_points": ("Обход в глубину с метками disc/low (алгоритм Тарьяна)." if ru else
                                    "DFS with disc/low values (Tarjan's algorithm)."),
            "bridges": ("Обход в глубину с disc/low; ребро — мост, если low[w] > disc[u]." if ru else
                        "DFS with disc/low; an edge is a bridge if low[w] > disc[u]."),
            "negative_cycle": ("Беллман–Форд от виртуального истока; лишнее ослабление ⇒ отрицательный "
                               "цикл." if ru else
                               "Bellman–Ford from a virtual source; an extra relaxation ⇒ a negative "
                               "cycle."),
        }[self.task_type]
        if self.task_type == "negative_cycle":
            ans = ("да" if self.answer else "нет") if ru else ("yes" if self.answer else "no")
        else:
            ans = str(self.answer)
        self.final_answer = ans
        self.solution_steps = [steps, (f"Ответ: {ans}." if ru else f"Answer: {ans}.")]

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
