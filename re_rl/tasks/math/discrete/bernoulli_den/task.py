"""BernoulliDenTask — знаменатель числа Бернулли.

Для чётного индекса m не меньше 2 знаменатель — произведение простых p, у которых p-1 делит m.
Индекс растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    factor = 3
    while factor * factor <= number:
        if number % factor == 0:
            return False
        factor += 2
    return True


def bernoulli_den_trace(index: int) -> List[Tuple[int, int, int]]:
    denominator = 1
    count = 0
    trace = []
    for divisor in range(1, index + 1):
        used = 0
        if index % divisor == 0 and is_prime(divisor + 1):
            denominator *= divisor + 1
            count += 1
            used = 1
        trace.append((used, denominator, count))
    return trace


class BernoulliDenTask(BaseMathTask):
    TASK_TYPE = "bernoulli_den"
    TASK_TYPES = ["den", "count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = bernoulli_den_trace(self.n)
        self.den = self.trace[-1][1]
        self.count = self.trace[-1][2]
        library = abs(int(sp.bernoulli(self.n).as_numer_denom()[1]))
        assert self.den == library
        self.answer = self.den if self.task_type == "den" else self.count
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "den" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, d=index, used=used, den=den, count=count)
            for index, (used, den, count) in enumerate(self.trace, 1)
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
