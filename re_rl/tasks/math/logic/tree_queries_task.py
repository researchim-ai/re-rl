"""TreeQueriesTask — запросы к дереву.

Дерево задаётся списком рёбер, корень — вершина 1.

Подтипы:
- ``diameter`` — число рёбер в самом длинном пути (дерево неориентированное);
- ``leaves``   — число листьев (вершин степени 1);
- ``height``   — высота от корня 1 (число рёбер до самой глубокой вершины);
- ``lca``      — наименьший общий предок двух вершин при корне 1.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class TreeQueriesTask(BaseMathTask):
    TASK_TYPE = "tree_queries"
    TASK_TYPES = ["diameter", "leaves", "height", "lca"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 6}, 3: {"n": 6}, 4: {"n": 7}, 5: {"n": 8},
        6: {"n": 9}, 7: {"n": 10}, 8: {"n": 11}, 9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.parents = {}
        edges = []
        for v in range(2, self.n + 1):
            parent = random.randint(1, v - 1)
            self.parents[v] = parent
            edges.append((parent, v))
        self.edges = edges
        self.adj = {i: [] for i in range(1, self.n + 1)}
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        if self.task_type == "diameter":
            self.ends, self.answer = self.diameter(self.adj)
        elif self.task_type == "leaves":
            self.leaf_nodes = sorted(v for v in range(1, self.n + 1) if len(self.adj[v]) == 1)
            self.answer = len(self.leaf_nodes)
        elif self.task_type == "height":
            self.depths = {1: 0}
            for v in range(2, self.n + 1):
                self.depths[v] = self.depths[self.parents[v]] + 1
            self.answer = max(self.depths.values())
        else:
            self.a, self.b = random.sample(range(1, self.n + 1), 2)
            self.answer = self.lca(self.parents, self.a, self.b)

    @staticmethod
    def _farthest(adj: Dict[int, List[int]], start: int) -> Tuple[int, Dict[int, int]]:
        dist = {start: 0}
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        far = max(dist, key=dist.get)
        return far, dist

    @classmethod
    def diameter(cls, adj) -> Tuple[Tuple[int, int], int]:
        far, _ = cls._farthest(adj, 1)
        other, dist = cls._farthest(adj, far)
        return (far, other), dist[other]

    @staticmethod
    def lca(parents: Dict[int, int], a: int, b: int) -> int:
        def ancestors(x: int) -> List[int]:
            chain = []
            while x != 1:
                chain.append(x)
                x = parents[x]
            chain.append(1)
            return chain

        seen = set(ancestors(b))
        for x in ancestors(a):
            if x in seen:
                return x
        return 1

    def _edge_str(self) -> str:
        return ", ".join(f"{u}-{v}" for u, v in self.edges)

    def _descr(self, language):
        ru = language == "ru"
        edges = self._edge_str()
        head = ((f"Дано дерево с вершинами 1..{self.n} и рёбрами: {edges}. Корень — вершина 1.")
                if ru else
                (f"A tree on vertices 1..{self.n} has edges: {edges}. The root is vertex 1."))
        if self.task_type == "diameter":
            ask = (("Сколько рёбер в самом длинном пути (диаметр)?") if ru else
                   ("How many edges are in a longest path (the diameter)?"))
        elif self.task_type == "leaves":
            ask = (("Сколько в дереве листьев (вершин степени 1)?") if ru else
                   ("How many leaves (degree-1 vertices) does the tree have?"))
        elif self.task_type == "height":
            ask = (("Какова высота дерева — число рёбер от корня до самой глубокой вершины?")
                   if ru else
                   ("What is the height — the number of edges from the root to the deepest vertex?"))
        else:
            ask = ((f"Найдите наименьший общий предок вершин {self.a} и {self.b}.") if ru else
                   (f"Find the lowest common ancestor of vertices {self.a} and {self.b}."))
        return f"{head} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "diameter":
            u, v = self.ends
            step = ((f"Два обхода в ширину: дальняя от 1 вершина и дальняя от неё — {u} и {v}, "
                     f"между ними {self.answer} рёбер.") if ru else
                    (f"Two BFS passes give endpoints {u} and {v}, with {self.answer} edges between them."))
        elif self.task_type == "leaves":
            listed = ", ".join(map(str, self.leaf_nodes))
            step = ((f"Вершины степени 1: {listed}.") if ru else
                    (f"Degree-1 vertices: {listed}."))
        elif self.task_type == "height":
            deep = max(self.depths, key=self.depths.get)
            step = ((f"Самая глубокая вершина — {deep}, глубина {self.answer}.") if ru else
                    (f"The deepest vertex is {deep}, at depth {self.answer}."))
        else:
            step = ((f"Поднимаемся от {self.a} и {self.b} к корню; первая общая вершина — {self.answer}.")
                    if ru else
                    (f"Walk from {self.a} and {self.b} toward the root; the first shared vertex is "
                     f"{self.answer}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
