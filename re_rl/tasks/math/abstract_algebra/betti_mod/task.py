"""BettiModTask — числа Бетти цепного комплекса по модулю 2.

Граница ребра — сумма его вершин, граница треугольника — сумма трёх рёбер.
Квадрат границы равен нулю. Число вершин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Edge = Tuple[int, int]
Face = Tuple[int, int, int]


def _rank(vectors: List[List[int]]) -> int:
    rows = [row[:] for row in vectors]
    rank = 0
    width = len(rows[0]) if rows else 0
    for col in range(width):
        pivot = None
        for index in range(rank, len(rows)):
            if rows[index][col]:
                pivot = index
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][col]:
                rows[index] = [left ^ right for left, right in zip(rows[index], rows[rank])]
        rank += 1
    return rank


def homology_trace(vertices: int, edges: Sequence[Edge], faces: Sequence[Face]) -> List[Tuple[int, int]]:
    parent = list(range(vertices + 1))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    components = vertices
    redundant = 0
    trace = []
    for left, right in edges:
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            redundant += 1
        else:
            parent[root_left] = root_right
            components -= 1
        trace.append((components, redundant))
    index = {edge: place for place, edge in enumerate(edges)}
    vectors = []
    betti = redundant
    for face in faces:
        one, two, three = face
        vector = [0] * len(edges)
        for pair in ((one, two), (two, three), (one, three)):
            vector[index[tuple(sorted(pair))]] ^= 1
        vectors.append(vector)
        rank = _rank(vectors)
        betti = redundant - rank
        trace.append((components, betti))
    if betti < 0:
        raise RuntimeError("betti mismatch")
    return trace


class BettiModTask(BaseMathTask):
    TASK_TYPE = "betti_mod"
    TASK_TYPES = ["b0", "b1"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        cycle = [(index, index + 1) for index in range(1, self.n)]
        cycle.append((1, self.n))
        extra = []
        edge_set = set(cycle)
        for _ in range(self.n // 2):
            left, right = random.sample(range(1, self.n + 1), 2)
            pair = tuple(sorted((left, right)))
            if pair not in edge_set:
                edge_set.add(pair)
                extra.append(pair)
        self.edges = cycle + extra
        self.faces = []
        for one in range(1, self.n + 1):
            for two in range(one + 1, self.n + 1):
                for three in range(two + 1, self.n + 1):
                    pairs = (tuple(sorted((one, two))), tuple(sorted((two, three))), tuple(sorted((one, three))))
                    if all(pair in edge_set for pair in pairs):
                        self.faces.append((one, two, three))
        self.trace = homology_trace(self.n, self.edges, self.faces)
        self.b0 = self.trace[-1][0]
        self.b1 = self.trace[-1][1]
        self.answer = self.b0 if self.task_type == "b0" else self.b1
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _edges(self) -> str:
        return "; ".join(f"{left} {right}" for left, right in self.edges)

    def _faces(self) -> str:
        if not self.faces:
            return "0"
        return "; ".join(f"{one} {two} {three}" for one, two, three in self.faces)

    def _descr(self, language):
        key = "s0" if self.task_type == "b0" else "s1"
        return texts.t(key, language, n=self.n, edges=self._edges(), faces=self._faces())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, b0=b0, b1=b1)
            for index, (b0, b1) in enumerate(self.trace, 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
