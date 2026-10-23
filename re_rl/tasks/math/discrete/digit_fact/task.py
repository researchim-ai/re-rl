"""DigitFactTask — сумма факториалов десятичных цифр.

0! = 1. Число шагов растёт с уровнем, на каждом шаге число заменяется этой суммой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

FACTORIALS = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880)


def digit_fact_trace(start: int, rounds: int) -> List[int]:
    value = start
    trace = []
    for _ in range(rounds):
        value = sum(FACTORIALS[int(symbol)] for symbol in str(value))
        trace.append(value)
    return trace


class DigitFactTask(BaseMathTask):
    TASK_TYPE = "digit_fact"
    TASK_TYPES = ["value", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "d": 2}, 2: {"n": 2, "d": 2}, 3: {"n": 3, "d": 3},
        4: {"n": 3, "d": 3}, 5: {"n": 4, "d": 3}, 6: {"n": 5, "d": 4},
        7: {"n": 6, "d": 4}, 8: {"n": 7, "d": 4}, 9: {"n": 8, "d": 5},
        10: {"n": 10, "d": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        digits = max(2, int(p["d"]))
        self.start = random.randint(10 ** (digits - 1), 10 ** digits - 1)
        self.trace = digit_fact_trace(self.start, self.n)
        self.value = self.trace[-1]
        self.peak = max([self.start, *self.trace])
        self.answer = self.value if self.task_type == "value" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, start=self.start, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.trace, 1)
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
