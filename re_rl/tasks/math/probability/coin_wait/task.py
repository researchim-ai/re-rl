"""CoinWaitTask — среднее число бросков до первого появления двоичного слова.

Для каждой длины, у которой конец совпадает с началом, к ожиданию прибавляется степень двойки.
Длина слова растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _markov_wait(pattern: Sequence[int]) -> Fraction:
    length = len(pattern)
    size = length

    def follow(state: int, bit: int) -> int:
        word = tuple(pattern[:state]) + (bit,)
        for width in range(len(word), 0, -1):
            if word[-width:] == tuple(pattern[:width]):
                return width
        return 0

    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    right = [Fraction(1) for _ in range(size)]
    for state in range(size):
        matrix[state][state] += 1
        for bit in (0, 1):
            nxt = follow(state, bit)
            if nxt < size:
                matrix[state][nxt] -= Fraction(1, 2)
    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col] != 0)
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        right[col], right[pivot] = right[pivot], right[col]
        scale = matrix[col][col]
        for col2 in range(col, size):
            matrix[col][col2] /= scale
        right[col] /= scale
        for row in range(size):
            if row == col or matrix[row][col] == 0:
                continue
            factor = matrix[row][col]
            for col2 in range(col, size):
                matrix[row][col2] -= factor * matrix[col][col2]
            right[row] -= factor * right[col]
    return right[0]


def coin_trace(pattern: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    borders = 0
    trace = []
    for width in range(1, len(pattern) + 1):
        added = 0
        if tuple(pattern[-width:]) == tuple(pattern[:width]):
            added = 1 << width
            borders += 1
        total += added
        trace.append((added, total, borders))
    if borders < 1 or total != _markov_wait(pattern):
        raise RuntimeError("wait mismatch")
    return trace


class CoinWaitTask(BaseMathTask):
    TASK_TYPE = "coin_wait"
    TASK_TYPES = ["wait", "borders"]

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
        self.pattern = tuple(random.randint(0, 1) for _ in range(self.n))
        self.trace = coin_trace(self.pattern)
        self.wait = self.trace[-1][1]
        self.borders = self.trace[-1][2]
        self.answer = self.wait if self.task_type == "wait" else self.borders
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(bit) for bit in self.pattern)

    def _descr(self, language):
        key = "s0" if self.task_type == "wait" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, added=added, wait=wait, borders=borders)
            for index, (added, wait, borders) in enumerate(self.trace, 1)
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
