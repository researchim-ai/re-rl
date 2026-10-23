"""PermanentTask — перманент матрицы из нулей и единиц.

Перманент считается по формуле Райзера: сумма по наборам столбцов.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def permanent_trace(matrix: Sequence[Sequence[int]]) -> List[int]:
    size = len(matrix)
    total = 0
    trace = []
    for mask in range(1 << size):
        bits = 0
        product = 1
        for row in matrix:
            column_sum = 0
            for col, bit in enumerate(row):
                if mask >> col & 1:
                    column_sum += bit
            product *= column_sum
        for col in range(size):
            if mask >> col & 1:
                bits += 1
        sign = 1 if (size - bits) % 2 == 0 else -1
        total += sign * product
        trace.append(total)
    return trace


class PermanentTask(BaseMathTask):
    TASK_TYPE = "permanent"
    TASK_TYPES = ["value", "parity"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        order = list(range(self.n))
        random.shuffle(order)
        self.matrix = [[0] * self.n for _ in range(self.n)]
        for row, col in enumerate(order):
            self.matrix[row][col] = 1
        for row in range(self.n):
            for col in range(self.n):
                if self.matrix[row][col] == 0 and random.randint(0, 2) == 0:
                    self.matrix[row][col] = 1
        self.trace = permanent_trace(self.matrix)
        self.value = self.trace[-1]
        self.parity = self.value % 2
        self.answer = self.value if self.task_type == "value" else self.parity
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(" ".join(str(bit) for bit in row) for row in self.matrix)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, total=total)
            for index, total in enumerate(self.trace, 1)
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
