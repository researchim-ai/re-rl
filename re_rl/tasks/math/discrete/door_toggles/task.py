"""DoorTogglesTask — двери, которые переключают проходы 1..n.

Дверь k остаётся открытой тогда и только тогда, когда у k нечётное число делителей.
Число дверей растёт с уровнем, решение идёт по каждой двери.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
from typing import Any, ClassVar, Dict, List

import random

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _divisor_count(number: int) -> int:
    count = 0
    divisor = 1
    while divisor * divisor <= number:
        if number % divisor == 0:
            count += 1 if divisor * divisor == number else 2
        divisor += 1
    return count


class DoorTogglesTask(BaseMathTask):
    TASK_TYPE = "door_toggles"
    TASK_TYPES = ["count", "largest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 8},
        6: {"n": 9}, 7: {"n": 12}, 8: {"n": 14}, 9: {"n": 15}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.divisors: List[int] = [_divisor_count(door) for door in range(1, self.n + 1)]
        self.open_flags = [count % 2 == 1 for count in self.divisors]
        self.count = sum(self.open_flags)
        self.largest = max(door for door, flag in enumerate(self.open_flags, 1) if flag)
        self.answer = self.count if self.task_type == "count" else self.largest
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = []
        for door, count in enumerate(self.divisors, 1):
            state = texts.t("s4" if count % 2 else "s5", self.language)
            steps.append(texts.t("s2", self.language, i=door, divisors=count, state=state))
        steps.append(texts.t("s3", self.language, count=self.count, largest=self.largest))
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


def open_count(n: int) -> int:
    return math.isqrt(n)
