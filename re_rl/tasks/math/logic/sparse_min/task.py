"""SparseMinTask — минимум на отрезке по разреженной таблице.

Уровень 0 — сам массив. Уровень t хранит минимумы блоков длины 2^t.
Длина массива растёт с уровнем сложности, построение идёт за O(n log n).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def build_sparse(values: Sequence[int]) -> List[List[int]]:
    table = [list(values)]
    span = 1
    size = len(values)
    while span * 2 <= size:
        previous = table[-1]
        span *= 2
        half = span // 2
        row = [
            min(previous[index], previous[index + half])
            for index in range(size - span + 1)
        ]
        table.append(row)
    return table


def sparse_min(table: Sequence[Sequence[int]], left: int, right: int) -> int:
    length = right - left + 1
    level = length.bit_length() - 1
    span = 1 << level
    return min(table[level][left], table[level][right - span + 1])


class SparseMinTask(BaseMathTask):
    TASK_TYPE = "sparse_min"
    TASK_TYPES = ["range", "cell"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(4, int(p["n"]))
        self.values = [random.randint(0, 20) for _ in range(self.n)]
        self.table = build_sparse(self.values)
        self.left = random.randint(1, self.n)
        self.right = random.randint(self.left, self.n)
        self.range_min = sparse_min(self.table, self.left - 1, self.right - 1)
        self.level = random.randint(1, len(self.table) - 1)
        self.index = random.randint(1, len(self.table[self.level]))
        self.cell = self.table[self.level][self.index - 1]
        self.answer = self.range_min if self.task_type == "range" else self.cell
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        if self.task_type == "range":
            return texts.t("s0", language, n=self.n, listing=listing, left=self.left, right=self.right)
        return texts.t(
            "s1", language, n=self.n, listing=listing, level=self.level, index=self.index,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.values, 1)
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
