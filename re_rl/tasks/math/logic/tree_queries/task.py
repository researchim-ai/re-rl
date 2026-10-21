"""TreeQueriesTask — запросы к дереву.

Дерево задаётся списком рёбер, корень — вершина 1.

Подтипы:
- ``diameter`` — число рёбер в самом длинном пути (дерево неориентированное);
- ``leaves``   — число листьев (вершин степени 1);
- ``height``   — высота от корня 1 (число рёбер до самой глубокой вершины);
- ``lca``      — наименьший общий предок двух вершин при корне 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        edges = self._edge_str()
        head = ((texts.t('s0', language, n=self.n, edges=edges)))
        if self.task_type == "diameter":
            ask = ((texts.t('s1', language)))
        elif self.task_type == "leaves":
            ask = ((texts.t('s3', language)))
        elif self.task_type == "height":
            ask = ((texts.t('s5', language)))
        else:
            ask = ((texts.t('s6', language, a=self.a, b=self.b)))
        return f"{head} {ask}"

    def solve(self):
        if self.task_type == "diameter":
            u, v = self.ends
            step = ((texts.t('s2', self.language, u=u, v=v, answer=self.answer)))
        elif self.task_type == "leaves":
            listed = ", ".join(map(str, self.leaf_nodes))
            step = ((texts.t('s4', self.language, listed=listed)))
        elif self.task_type == "height":
            deep = max(self.depths, key=self.depths.get)
            step = ((texts.t('s7', self.language, deep=deep, answer=self.answer)))
        else:
            step = ((texts.t('s8', self.language, a=self.a, b=self.b, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
