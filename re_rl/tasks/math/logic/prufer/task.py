"""PruferTask — код Прюфера дерева.

Код строится жадно: на каждом шаге удаляется лист с наименьшим номером,
в код пишется его единственный сосед. Длина кода n-2.
Степень вершины равна 1 плюс число её вхождений в код.

Подтипы: сам код и степень вершины.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import heapq
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def prufer_encode(n: int, edges: List[Tuple[int, int]]) -> List[int]:
    adj = [set() for _ in range(n + 1)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    degree = [0] * (n + 1)
    for v in range(1, n + 1):
        degree[v] = len(adj[v])
    leaves = [v for v in range(1, n + 1) if degree[v] == 1]
    heapq.heapify(leaves)
    code = []
    for _ in range(n - 2):
        leaf = heapq.heappop(leaves)
        while degree[leaf] != 1:
            leaf = heapq.heappop(leaves)
        neighbor = next(iter(adj[leaf]))
        code.append(neighbor)
        adj[leaf].remove(neighbor)
        adj[neighbor].remove(leaf)
        degree[leaf] -= 1
        degree[neighbor] -= 1
        if degree[neighbor] == 1:
            heapq.heappush(leaves, neighbor)
    return code


class PruferTask(BaseMathTask):
    TASK_TYPE = "prufer_code"
    TASK_TYPES = ["encode", "degree"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9}, 9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        raw = [(random.randint(1, v - 1), v) for v in range(2, self.n + 1)]
        self.edges = sorted((min(a, b), max(a, b)) for a, b in raw)
        self.code = prufer_encode(self.n, self.edges)
        self.vertex = random.randint(1, self.n)
        self.degree = 1 + self.code.count(self.vertex)
        edge_degree = sum(1 for a, b in self.edges if a == self.vertex or b == self.vertex)
        if edge_degree != self.degree:
            raise RuntimeError(texts.t('s5', language))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{a}-{b}" for a, b in self.edges)
        rule = ((texts.t('s0', language)))
        if self.task_type == "encode":
            ask = ((texts.t('s1', language, n=self.n, shown=shown)))
        else:
            ask = ((texts.t('s2', language, n=self.n, shown=shown, vertex=self.vertex)))
        return f"{rule} {ask}"

    def solve(self):
        code = ", ".join(map(str, self.code))
        if self.task_type == "encode":
            step = ((texts.t('s3', self.language, code=code)))
            self.final_answer = code
        else:
            step = ((texts.t('s4', self.language, vertex=self.vertex, v1=self.code.count(self.vertex), degree=self.degree)))
            self.final_answer = str(self.degree)
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.final_answer)))]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "degree":
            return U.verify_int(prediction, self.degree)
        return U.verify_int_sequence(prediction, self.code)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
