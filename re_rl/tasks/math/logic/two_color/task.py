"""TwoColorTask — последовательная раскраска графа в два цвета.

Вершина получает цвет соседа, если он один. Два разных цвета соседей — конфликт.
Число вершин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Edge = Tuple[int, int]


def color_trace(vertices: int, edges: Sequence[Edge]) -> List[Tuple[int, int, int]]:
    neighbors: List[List[int]] = [[] for _ in range(vertices + 1)]
    for src, dst in edges:
        neighbors[src].append(dst)
        neighbors[dst].append(src)
    color = [0] * (vertices + 1)
    conflicts = 0
    first = 0
    trace = []
    for vertex in range(1, vertices + 1):
        used = {color[other] for other in neighbors[vertex] if color[other]}
        if used == {1}:
            color[vertex] = 2
        elif used == {2}:
            color[vertex] = 1
        elif not used:
            color[vertex] = 1
        else:
            conflicts += 1
            if first == 0:
                first = vertex
        trace.append((color[vertex], conflicts, first))
    return trace


class TwoColorTask(BaseMathTask):
    TASK_TYPE = "two_color"
    TASK_TYPES = ["conflicts", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        edges = set()
        tries = 0
        while len(edges) < self.n and tries < self.n * 8:
            tries += 1
            src = random.randint(1, self.n)
            dst = random.randint(1, self.n)
            if src != dst:
                edges.add((min(src, dst), max(src, dst)))
        self.edges = sorted(edges)
        self.trace = color_trace(self.n, self.edges)
        _, self.conflicts, self.first = self.trace[-1]
        self.answer = self.conflicts if self.task_type == "conflicts" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{src} {dst}" for src, dst in self.edges)
        key = "s0" if self.task_type == "conflicts" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, color=color, conflicts=conflicts, first=first)
            for index, (color, conflicts, first) in enumerate(self.trace, 1)
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
