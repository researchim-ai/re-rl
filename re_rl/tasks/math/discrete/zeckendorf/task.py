"""ZeckendorfTask — жадная запись суммой чисел Фибоначчи без соседей.

Берём наибольшее подходящее число Фибоначчи и не ставим два соседних.
Число доступных чисел Фибоначчи растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fibonacci_list(count: int) -> List[int]:
    vals = [1, 2]
    while len(vals) < count:
        vals.append(vals[-1] + vals[-2])
    return vals[:count]


def zeckendorf_trace(number: int, fibs: Sequence[int]) -> List[Tuple[int, int, int]]:
    left = number
    trace = []
    for fib in reversed(fibs):
        take = 1 if fib <= left else 0
        if take:
            left -= fib
        trace.append((fib, take, left))
    return trace


class ZeckendorfTask(BaseMathTask):
    TASK_TYPE = "zeckendorf"
    TASK_TYPES = ["weight", "bit"]

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
        self.n = max(3, int(p["n"]))
        self.fibs = fibonacci_list(self.n)
        limit = self.fibs[-1] + self.fibs[-2] - 1
        self.number = random.randint(1, max(1, limit))
        self.trace = zeckendorf_trace(self.number, self.fibs)
        self.takes = [take for _, take, _ in reversed(self.trace)]
        self.weight = sum(self.takes)
        self.k = random.randint(1, self.n)
        self.bit = self.takes[self.k - 1]
        self.answer = self.weight if self.task_type == "weight" else self.bit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.fibs)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, number=self.number, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, fib=fib, take=take, left=left)
            for index, (fib, take, left) in enumerate(self.trace, 1)
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
