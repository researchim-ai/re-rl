"""UnionCountTask — объединение элементов в группы.

Сначала каждый элемент сам по себе. Связь сливает группы двух элементов. Повторная связь внутри группы ничего не меняет.
Число связей равно числу элементов и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def link_trace(size: int, pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    parent = list(range(size))

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    parts = size
    joined = 0
    trace = []
    for left, right in pairs:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_left] = root_right
            parts -= 1
            joined += 1
        trace.append((parts, joined))
    return trace


class UnionCountTask(BaseMathTask):
    TASK_TYPE = "union_count"
    TASK_TYPES = ["parts", "joined"]

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
        self.n = max(2, int(p["n"]))
        self.pairs = [
            (random.randint(0, self.n - 1), random.randint(0, self.n - 1))
            for _ in range(self.n)
        ]
        self.trace = link_trace(self.n, self.pairs)
        self.parts = self.trace[-1][0]
        self.joined = self.trace[-1][1]
        self.answer = self.parts if self.task_type == "parts" else self.joined
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{left} {right}" for left, right in self.pairs)
        key = "s0" if self.task_type == "parts" else "s1"
        return texts.t(key, language, n=self.n, pairs=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, parts=parts, joined=joined)
            for index, ((left, right), (parts, joined)) in enumerate(zip(self.pairs, self.trace), 1)
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
