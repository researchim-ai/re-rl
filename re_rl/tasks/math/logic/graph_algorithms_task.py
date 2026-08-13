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

import heapq
import random
from collections import defaultdict, deque
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _GraphBase(BaseMathTask):
    """Общие мелочи для графовых задач."""

    def _finish(self, description, language, detail_level, output_format, reasoning_mode):
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class WeightedShortestPathTask(_GraphBase):
    TASK_TYPE = "weighted_shortest_path"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "wmax": 6}, 2: {"n": 5, "wmax": 8}, 3: {"n": 5, "wmax": 9},
        4: {"n": 6, "wmax": 9}, 5: {"n": 7, "wmax": 9}, 6: {"n": 8, "wmax": 12},
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
        self.edges: List[Tuple[int, int, int]] = []
        adj = defaultdict(list)
        perm = list(range(n))
        random.shuffle(perm)
        for i in range(1, n):  # остовное дерево — связность
            a, b = perm[i], perm[random.randrange(i)]
            w = random.randint(1, self.wmax)
            self.edges.append((a, b, w)); adj[a].append((b, w)); adj[b].append((a, w))
        for _ in range(n):
            a, b = random.sample(range(n), 2)
            w = random.randint(1, self.wmax)
            self.edges.append((a, b, w)); adj[a].append((b, w)); adj[b].append((a, w))
        self.adj = adj
        self.src, self.dst = random.sample(range(n), 2)
        self._answer = self._dijkstra()

    def _dijkstra(self):
        dist = {self.src: 0}
        pq = [(0, self.src)]
        while pq:
            d, v = heapq.heappop(pq)
            if d > dist.get(v, 1e18):
                continue
            for w, wt in self.adj[v]:
                nd = d + wt
                if nd < dist.get(w, 1e18):
                    dist[w] = nd
                    heapq.heappush(pq, (nd, w))
        return dist.get(self.dst, -1)

    def _edges_str(self):
        return ", ".join(f"({a}-{b}, вес {w})" for a, b, w in self.edges)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Взвешенный неориентированный граф (вершины 0..{self.n-1}). Рёбра: {self._edges_str()}.\n"
                 f"Найдите вес кратчайшего пути между вершинами {self.src} и {self.dst}.") if ru else
                (f"Weighted undirected graph (vertices 0..{self.n-1}). Edges: "
                 + ", ".join(f"({a}-{b}, w {w})" for a, b, w in self.edges) +
                 f".\nFind the weight of the shortest path between vertices {self.src} and {self.dst}."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Алгоритм Дейкстры: жадно расширяем множество вершин с известным минимальным расстоянием." if ru else
             "Dijkstra's algorithm: greedily settle vertices with known minimum distance."),
            (f"Кратчайшее расстояние = {self._answer}." if ru else f"Shortest distance = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


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
        ru = language == "ru"
        head = (f"Ориентированный граф (вершины 0..{self.n-1}). Дуги: {self._edges_str()}." if ru else
                f"Directed graph (vertices 0..{self.n-1}). Arcs: {self._edges_str()}.")
        if self.subtype == "has_cycle":
            q = (" Есть ли в графе ориентированный цикл? Ответьте да/нет." if ru else
                 " Does the graph contain a directed cycle? Answer yes/no.")
        else:
            q = (" Выпишите топологический порядок вершин (слева направо)." if ru else
                 " Output a topological ordering of the vertices (left to right).")
        return head + q

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "has_cycle":
            self.solution_steps = [
                ("Алгоритм Кана: удаляем вершины с нулевой полустепенью захода." if ru else
                 "Kahn's algorithm: repeatedly remove vertices with in-degree zero."),
                ((("Обработать все вершины не удалось — цикл есть." if self._cycle else
                   "Все вершины обработаны — цикла нет.")) if ru else
                 (("Not all vertices could be processed — there is a cycle." if self._cycle else
                   "All vertices processed — no cycle."))),
            ]
            self.final_answer = ("да" if self._cycle else "нет") if ru else ("yes" if self._cycle else "no")
        else:
            order = self._topo_order()
            self.solution_steps = [
                ("Повторно берём вершину без входящих дуг и удаляем её." if ru else
                 "Repeatedly take a vertex with no incoming arcs and remove it."),
                (f"Один из порядков: {', '.join(map(str, order))}." if ru else
                 f"One valid order: {', '.join(map(str, order))}."),
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
        self.subtype = subtype or random.choice(self.TASK_TYPES)
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
        return ", ".join(f"({a}-{b})" for a, b in self.edges) or "нет рёбер"

    def _descr(self, language):
        ru = language == "ru"
        head = (f"Неориентированный граф (вершины 0..{self.n-1}). Рёбра: {self._edges_str()}." if ru else
                f"Undirected graph (vertices 0..{self.n-1}). Edges: "
                + (", ".join(f"({a}-{b})" for a, b in self.edges) or "no edges") + ".")
        if self.subtype == "chromatic":
            q = (" Найдите хроматическое число (минимальное число цветов правильной раскраски)." if ru else
                 " Find the chromatic number (minimum number of colors for a proper coloring).")
        else:
            q = (f" Можно ли правильно раскрасить граф в {self.k} цвета? Ответьте да/нет." if ru else
                 f" Can the graph be properly colored with {self.k} colors? Answer yes/no.")
        return head + q

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "chromatic":
            self.solution_steps = [
                ("Ищем наименьшее k, для которого существует правильная k-раскраска (перебор с возвратом)." if ru else
                 "Find the smallest k admitting a proper k-coloring (backtracking)."),
                (f"Хроматическое число = {self.chromatic}." if ru else f"Chromatic number = {self.chromatic}."),
            ]
            self.final_answer = str(self.chromatic)
        else:
            self.solution_steps = [
                (f"Проверяем существование правильной раскраски в {self.k} цветов." if ru else
                 f"Check whether a proper {self.k}-coloring exists."),
                ((f"Хроматическое число = {self.chromatic}, поэтому "
                  + ("возможно." if self._answer_bool else "невозможно.")) if ru else
                 (f"Chromatic number = {self.chromatic}, so it is "
                  + ("possible." if self._answer_bool else "impossible."))),
            ]
            self.final_answer = ("да" if self._answer_bool else "нет") if ru else ("yes" if self._answer_bool else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "chromatic":
            return U.verify_int(prediction, int(self.chromatic))
        return U.verify_bool(prediction, bool(self._answer_bool))


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
        ru = language == "ru"
        es = ", ".join(f"({a}-{b}, вес {w})" for a, b, w in self.edges)
        return ((f"Взвешенный связный граф (вершины 0..{self.n-1}). Рёбра: {es}.\n"
                 f"Найдите суммарный вес минимального остовного дерева.") if ru else
                (f"Weighted connected graph (vertices 0..{self.n-1}). Edges: "
                 + ", ".join(f"({a}-{b}, w {w})" for a, b, w in self.edges) +
                 ".\nFind the total weight of the minimum spanning tree."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Алгоритм Крускала: сортируем рёбра по весу и добавляем, если не образуется цикл." if ru else
             "Kruskal's algorithm: sort edges by weight, add each if it does not create a cycle."),
            (f"Вес минимального остовного дерева = {self._answer}." if ru else
             f"Minimum spanning tree weight = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


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
        ru = language == "ru"
        es = ", ".join(f"({a}-{b})" for a, b in self.edges)
        return ((f"Неориентированный граф (вершины 0..{self.n-1}). Рёбра: {es}.\n"
                 f"Существует ли эйлеров путь (проходящий по каждому ребру ровно один раз)? Ответьте да/нет.") if ru else
                (f"Undirected graph (vertices 0..{self.n-1}). Edges: {es}.\n"
                 f"Does an Eulerian path (using every edge exactly once) exist? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Эйлеров путь существует, если граф связен (по рёбрам) и число вершин нечётной степени равно 0 или 2." if ru else
             "An Eulerian path exists iff the graph is connected (over edges) and has 0 or 2 odd-degree vertices."),
            ((("Условие выполнено — путь существует." if self._answer else
               "Условие нарушено — пути нет.")) if ru else
             (("Condition holds — a path exists." if self._answer else
               "Condition fails — no path."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))


class HamiltonianPathTask(_GraphBase):
    TASK_TYPE = "hamiltonian_path"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 8}, 10: {"n": 9},
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
        for a in range(n):
            for b in range(a + 1, n):
                if random.random() < 0.45:
                    self.edges.append((a, b))
        self._answer = self._has_hamiltonian()

    def _has_hamiltonian(self):
        adj = defaultdict(set)
        for a, b in self.edges:
            adj[a].add(b); adj[b].add(a)
        n = self.n
        # ДП по битовым маскам: dp[mask][v] — можно ли покрыть mask, закончив в v.
        dp = [[False] * n for _ in range(1 << n)]
        for v in range(n):
            dp[1 << v][v] = True
        for mask in range(1 << n):
            for v in range(n):
                if not dp[mask][v]:
                    continue
                for w in adj[v]:
                    if not (mask >> w) & 1:
                        dp[mask | (1 << w)][w] = True
        full = (1 << n) - 1
        return any(dp[full][v] for v in range(n))

    def _descr(self, language):
        ru = language == "ru"
        es = ", ".join(f"({a}-{b})" for a, b in self.edges) or ("нет рёбер" if ru else "no edges")
        return ((f"Неориентированный граф (вершины 0..{self.n-1}). Рёбра: {es}.\n"
                 f"Существует ли гамильтонов путь (проходящий через каждую вершину ровно один раз)? Ответьте да/нет.") if ru else
                (f"Undirected graph (vertices 0..{self.n-1}). Edges: {es}.\n"
                 f"Does a Hamiltonian path (visiting every vertex exactly once) exist? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Перебираем пути с помощью ДП по подмножествам посещённых вершин." if ru else
             "Search paths via dynamic programming over subsets of visited vertices."),
            ((("Гамильтонов путь найден." if self._answer else "Гамильтонова пути нет.")) if ru else
             (("A Hamiltonian path exists." if self._answer else "No Hamiltonian path."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))


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
        ru = language == "ru"
        es = ", ".join(f"(L{l}-R{r})" for l, r in self.pairs) or ("нет рёбер" if ru else "no edges")
        return ((f"Двудольный граф: слева L0..L{self.L-1}, справа R0..R{self.R-1}. Допустимые пары: {es}.\n"
                 f"Найдите размер максимального паросочетания.") if ru else
                (f"Bipartite graph: left L0..L{self.L-1}, right R0..R{self.R-1}. Allowed pairs: {es}.\n"
                 f"Find the size of the maximum matching."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Алгоритм Куна: ищем увеличивающие пути для каждой левой вершины." if ru else
             "Kuhn's algorithm: find augmenting paths for each left vertex."),
            (f"Максимальное паросочетание = {self._answer}." if ru else
             f"Maximum matching = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


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
        ru = language == "ru"
        lines = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                lines.append(f"{a}-{b}: {self.d[a][b]}")
        table = "; ".join(lines)
        return ((f"{self.n} городов (0..{self.n-1}), симметричные расстояния: {table}.\n"
                 f"Найдите длину кратчайшего замкнутого маршрута, проходящего через все города по разу "
                 f"и возвращающегося в старт.") if ru else
                (f"{self.n} cities (0..{self.n-1}), symmetric distances: {table}.\n"
                 f"Find the length of the shortest closed tour visiting every city once and returning "
                 f"to the start."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Перебираем все перестановки городов и выбираем минимальную длину цикла." if ru else
             "Enumerate all city permutations and pick the minimum cycle length."),
            (f"Длина кратчайшего маршрута = {self._answer}." if ru else
             f"Shortest tour length = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


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
        ru = language == "ru"
        es = ", ".join(f"{a}→{b} (c={c})" for a, b, c in self.cap_edges)
        return ((f"Транспортная сеть (вершины 0..{self.n-1}), исток {self.s}, сток {self.t}. "
                 f"Ориентированные дуги с пропускными способностями: {es}.\n"
                 f"Найдите величину максимального потока из истока в сток.") if ru else
                (f"Flow network (vertices 0..{self.n-1}), source {self.s}, sink {self.t}. "
                 f"Directed arcs with capacities: {es}.\nFind the maximum flow value from source to sink."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Алгоритм Эдмондса–Карпа: ищем дополняющие пути BFS в остаточной сети." if ru else
             "Edmonds–Karp: find augmenting paths via BFS in the residual network."),
            (f"Максимальный поток = {self._answer}." if ru else f"Maximum flow = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


class DAGLongestPathTask(_GraphBase):
    TASK_TYPE = "dag_longest_path"
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
        ru = language == "ru"
        es = ", ".join(f"{a}→{b} (вес {w})" for a, b, w in self.edges)
        return ((f"Взвешенный ориентированный ациклический граф (вершины 0..{self.n-1}). Дуги: {es}.\n"
                 f"Найдите вес самого длинного пути (сумму весов дуг).") if ru else
                (f"Weighted directed acyclic graph (vertices 0..{self.n-1}). Arcs: "
                 + ", ".join(f"{a}→{b} (w {w})" for a, b, w in self.edges) +
                 ".\nFind the weight of the longest path (sum of arc weights)."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Обрабатываем вершины в топологическом порядке и накапливаем максимум." if ru else
             "Process vertices in topological order, accumulating the maximum."),
            (f"Длиннейший путь = {self._answer}." if ru else f"Longest path = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
