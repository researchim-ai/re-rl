"""FenwickSumTask — точечные прибавления в дереве Фенвика.

Индексы с 1. В ячейку i прибавляется значение, затем i увеличивается на младший бит.
Число прибавлений растёт с уровнем. Сумма префикса и значение узла считаются за O(n log n).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Update = Tuple[int, int]


def fenwick_build(size: int, updates: Sequence[Update]) -> Tuple[List[int], List[int]]:
    tree = [0] * (size + 1)
    values = [0] * (size + 1)
    for index, delta in updates:
        values[index] += delta
        cursor = index
        while cursor <= size:
            tree[cursor] += delta
            cursor += cursor & -cursor
    return tree, values


def fenwick_prefix(tree: Sequence[int], index: int) -> int:
    total = 0
    while index > 0:
        total += tree[index]
        index -= index & -index
    return total


class FenwickSumTask(BaseMathTask):
    TASK_TYPE = "fenwick_sum"
    TASK_TYPES = ["prefix", "node"]

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
        self.updates = [
            (random.randint(1, self.n), random.randint(1, 5))
            for _ in range(self.n)
        ]
        self.tree, self.values = fenwick_build(self.n, self.updates)
        self.k = random.randint(1, self.n)
        self.prefix = fenwick_prefix(self.tree, self.k)
        self.node = self.tree[self.k]
        self.answer = self.prefix if self.task_type == "prefix" else self.node
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{index}, {delta}" for index, delta in self.updates)
        key = "s0" if self.task_type == "prefix" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        running = [0] * (self.n + 1)
        steps = []
        for step, (index, delta) in enumerate(self.updates, 1):
            running[index] += delta
            steps.append(texts.t(
                "s2", self.language, i=step, index=index, delta=delta,
                prefix=sum(running[1:self.k + 1]),
            ))
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
