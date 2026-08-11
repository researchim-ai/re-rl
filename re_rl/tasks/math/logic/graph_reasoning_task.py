"""GraphReasoningTask — алгоритмические рассуждения на графах.

Подтипы:
- shortest_path: длина кратчайшего пути между двумя вершинами (BFS), -1 если пути нет;
- num_components: число компонент связности;
- is_bipartite: является ли граф двудольным (да/нет).
Все ответы вычисляются собственными детерминированными алгоритмами.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GraphReasoningTask(BaseMathTask):
    TASK_TYPE = "graph_reasoning"
    TASK_TYPES = ["shortest_path", "num_components", "is_bipartite"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 1}, 2: {"n": 5, "extra": 1}, 3: {"n": 6, "extra": 2},
        4: {"n": 7, "extra": 2}, 5: {"n": 8, "extra": 3}, 6: {"n": 9, "extra": 3},
        7: {"n": 10, "extra": 4}, 8: {"n": 11, "extra": 5}, 9: {"n": 12, "extra": 6},
        10: {"n": 14, "extra": 7},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.extra = int(preset["extra"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        n = self.n
        self.adj: Dict[int, set] = {i: set() for i in range(n)}
        self.edges: List[Tuple[int, int]] = []

        def add_edge(a, b):
            if a != b and b not in self.adj[a]:
                self.adj[a].add(b)
                self.adj[b].add(a)
                self.edges.append((a, b))

        if self.subtype == "is_bipartite":
            # С вероятностью 50% строим заведомо двудольный граф.
            self._force_bipartite = random.random() < 0.5
            if self._force_bipartite:
                part = [random.randint(0, 1) for _ in range(n)]
                if len(set(part)) == 1:
                    part[0] ^= 1
                left = [i for i in range(n) if part[i] == 0]
                right = [i for i in range(n) if part[i] == 1]
                m = n + self.extra
                for _ in range(m):
                    add_edge(random.choice(left), random.choice(right))
            else:
                for _ in range(n + self.extra + 2):
                    add_edge(random.randrange(n), random.randrange(n))
        elif self.subtype == "num_components":
            # Несколько кластеров, чтобы компонент было больше одной.
            perm = list(range(n))
            random.shuffle(perm)
            k = random.randint(2, max(2, n // 3))
            cuts = sorted(random.sample(range(1, n), k - 1)) if n > k else [1]
            groups, prev = [], 0
            for c in cuts + [n]:
                groups.append(perm[prev:c])
                prev = c
            for g in groups:
                for i in range(1, len(g)):
                    add_edge(g[i - 1], g[random.randrange(i)])
        else:  # shortest_path
            perm = list(range(n))
            random.shuffle(perm)
            for i in range(1, n):  # связующее дерево гарантирует достижимость
                add_edge(perm[i], perm[random.randrange(i)])
            for _ in range(self.extra):
                add_edge(random.randrange(n), random.randrange(n))
            self.src, self.dst = random.sample(range(n), 2)

        self._answer = self._compute()

    def _bfs_dist(self, s, t):
        if s == t:
            return 0
        seen = {s}
        q = deque([(s, 0)])
        while q:
            v, d = q.popleft()
            for w in self.adj[v]:
                if w == t:
                    return d + 1
                if w not in seen:
                    seen.add(w)
                    q.append((w, d + 1))
        return -1

    def _components(self):
        seen, comps = set(), 0
        for s in range(self.n):
            if s in seen:
                continue
            comps += 1
            stack = [s]
            seen.add(s)
            while stack:
                v = stack.pop()
                for w in self.adj[v]:
                    if w not in seen:
                        seen.add(w)
                        stack.append(w)
        return comps

    def _is_bipartite(self):
        color = {}
        for s in range(self.n):
            if s in color:
                continue
            color[s] = 0
            q = deque([s])
            while q:
                v = q.popleft()
                for w in self.adj[v]:
                    if w not in color:
                        color[w] = color[v] ^ 1
                        q.append(w)
                    elif color[w] == color[v]:
                        return False
        return True

    def _compute(self):
        if self.subtype == "shortest_path":
            return self._bfs_dist(self.src, self.dst)
        if self.subtype == "num_components":
            return self._components()
        return self._is_bipartite()

    def _edges_str(self):
        return ", ".join(f"({a}-{b})" for a, b in self.edges) or ("нет рёбер")

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        head = (f"Неориентированный граф с вершинами 0..{self.n - 1}. Рёбра: {self._edges_str()}."
                if ru else
                f"Undirected graph with vertices 0..{self.n - 1}. Edges: {self._edges_str()}.")
        if self.subtype == "shortest_path":
            q = (f" Найдите длину кратчайшего пути между вершинами {self.src} и {self.dst} "
                 f"(число рёбер; -1, если пути нет)." if ru else
                 f" Find the length of the shortest path between vertices {self.src} and {self.dst} "
                 f"(number of edges; -1 if no path).")
        elif self.subtype == "num_components":
            q = " Сколько компонент связности в графе?" if ru else " How many connected components does the graph have?"
        else:
            q = " Является ли граф двудольным? Ответьте да/нет." if ru else " Is the graph bipartite? Answer yes/no."
        return head + q

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "shortest_path":
            self.solution_steps = [
                ("Запускаем поиск в ширину (BFS) из стартовой вершины." if ru else
                 "Run breadth-first search (BFS) from the source vertex."),
                (f"Кратчайшее расстояние от {self.src} до {self.dst} = {self._answer}." if ru else
                 f"Shortest distance from {self.src} to {self.dst} = {self._answer}."),
            ]
            self.final_answer = str(self._answer)
        elif self.subtype == "num_components":
            self.solution_steps = [
                ("Обходим граф (DFS/union-find), считая непересекающиеся группы вершин." if ru else
                 "Traverse the graph (DFS/union-find), counting disjoint vertex groups."),
                (f"Число компонент связности = {self._answer}." if ru else
                 f"Number of connected components = {self._answer}."),
            ]
            self.final_answer = str(self._answer)
        else:
            self.solution_steps = [
                ("Пробуем 2-раскраску BFS: соседи разного цвета." if ru else
                 "Attempt a 2-coloring via BFS: neighbors get opposite colors."),
                (("Конфликтов нет — граф двудольный." if self._answer else
                  "Найдено ребро между вершинами одного цвета — не двудольный.") if ru else
                 ("No conflicts — the graph is bipartite." if self._answer else
                  "Found an edge within one color class — not bipartite.")),
            ]
            self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.subtype == "is_bipartite":
            return U.verify_bool(prediction, bool(self._answer))
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
