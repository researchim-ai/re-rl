"""SigmaRowTask — сумма делителей и её накопление.

Для каждого числа от 1 до n складываются все положительные делители, включая 1 и само число.
Верхняя граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def sigma(number: int) -> int:
    total = 0
    divisor = 1
    while divisor * divisor <= number:
        if number % divisor == 0:
            total += divisor
            if divisor * divisor != number:
                total += number // divisor
        divisor += 1
    return total


def sigma_trace(limit: int) -> List[Tuple[int, int]]:
    running = 0
    trace = []
    for number in range(1, limit + 1):
        value = sigma(number)
        running += value
        trace.append((value, running))
    return trace


class SigmaRowTask(BaseMathTask):
    TASK_TYPE = "sigma_row"
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
        self.trace = sigma_trace(self.n)
        self.k = random.randint(1, self.n)
        self.at = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        assert self.at == int(sp.divisor_sigma(self.k))
        self.answer = self.total if self.task_type == "total" else self.at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, sigma=value, total=total)
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
