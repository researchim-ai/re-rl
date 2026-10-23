"""CantorPairTask — свёртка списка спариванием Кантора.

Пара (x, y) получает номер (x+y)*(x+y+1)/2 + y. Список сворачивается слева направо.
Число свёрток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cantor_pair(left: int, right: int) -> int:
    total = left + right
    return total * (total + 1) // 2 + right


def cantor_unpair(code: int) -> Tuple[int, int]:
    diagonal = (math.isqrt(8 * code + 1) - 1) // 2
    right = code - diagonal * (diagonal + 1) // 2
    left = diagonal - right
    return left, right


def cantor_fold(numbers: List[int]) -> List[int]:
    value = numbers[0]
    trace = []
    for item in numbers[1:]:
        value = cantor_pair(value, item)
        trace.append(value)
    restored = []
    current = value
    for _ in numbers[1:]:
        current, item = cantor_unpair(current)
        restored.append(item)
    restored.append(current)
    restored.reverse()
    assert restored == numbers
    return trace


class CantorPairTask(BaseMathTask):
    TASK_TYPE = "cantor_pair"
    TASK_TYPES = ["code", "part"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.numbers = [random.randint(0, 5) for _ in range(self.n + 1)]
        self.trace = cantor_fold(self.numbers)
        self.k = random.randint(1, self.n)
        self.code = self.trace[-1]
        self.part = self.trace[self.k - 1]
        self.answer = self.code if self.task_type == "code" else self.part
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "code" else "s1"
        listed = ", ".join(str(item) for item in self.numbers)
        return texts.t(key, language, n=self.n, numbers=listed, k=self.k)

    def solve(self):
        steps = []
        left = self.numbers[0]
        for index, (right, value) in enumerate(zip(self.numbers[1:], self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, left=left, right=right, value=value,
            ))
            left = value
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
