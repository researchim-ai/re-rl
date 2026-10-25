"""JordanTotTask — функция Жордана порядка 2.

Начинается с квадрата числа. Для каждого простого p значение делится на p^2 и умножается на p^2-1.
Верхняя граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mobius(number: int) -> int:
    if number == 1:
        return 1
    primes = 0
    value = number
    factor = 2
    while factor * factor <= value:
        if value % factor == 0:
            value //= factor
            if value % factor == 0:
                return 0
            primes += 1
        factor += 1 if factor == 2 else 2
    if value > 1:
        primes += 1
    return -1 if primes % 2 else 1


def jordan_two(number: int) -> int:
    value = number * number
    rest = number
    factor = 2
    while factor * factor <= rest:
        if rest % factor == 0:
            value = value // (factor * factor) * (factor * factor - 1)
            while rest % factor == 0:
                rest //= factor
        factor += 1 if factor == 2 else 2
    if rest > 1:
        value = value // (rest * rest) * (rest * rest - 1)
    check = 0
    divisor = 1
    while divisor * divisor <= number:
        if number % divisor == 0:
            check += mobius(divisor) * (number // divisor) ** 2
            if divisor * divisor != number:
                check += mobius(number // divisor) * divisor ** 2
        divisor += 1
    assert check == value
    return value


def jordan_trace(limit: int) -> List[Tuple[int, int]]:
    running = 0
    trace = []
    for number in range(1, limit + 1):
        value = jordan_two(number)
        running += value
        trace.append((value, running))
    return trace


class JordanTotTask(BaseMathTask):
    TASK_TYPE = "jordan_tot"
    TASK_TYPES = ["total", "at"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = jordan_trace(self.n)
        self.k = random.randint(1, self.n)
        self.at = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, total=total)
            for index, (value, total) in enumerate(self.trace, 1)
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
