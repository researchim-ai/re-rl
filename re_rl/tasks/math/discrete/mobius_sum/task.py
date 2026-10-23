"""MobiusSumTask — функция Мёбиуса и её частичные суммы.

Ноль, если в разложении есть квадрат. Иначе минус единица в степени числа простых.
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


def mobius_trace(limit: int) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for number in range(1, limit + 1):
        value = mobius(number)
        total += value
        trace.append((value, total))
    return trace


class MobiusSumTask(BaseMathTask):
    TASK_TYPE = "mobius_sum"
    TASK_TYPES = ["sum", "mu"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 9}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = mobius_trace(self.n)
        self.k = random.randint(1, self.n)
        self.mu = self.trace[self.k - 1][0]
        self.sum = self.trace[-1][1]
        self.answer = self.sum if self.task_type == "sum" else self.mu
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "sum" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, mu=mu, total=total)
            for index, (mu, total) in enumerate(self.trace, 1)
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
