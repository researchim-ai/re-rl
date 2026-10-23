"""ReverseAddTask — переворот десятичной записи и сложение.

Нули в начале перевёрнутого числа не пишутся: 100 переворачивается в 1.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def reverse_digits(value: int) -> int:
    return int(str(value)[::-1])


def reverse_add_trace(start: int, count: int) -> List[int]:
    value = start
    trace = []
    for _ in range(count):
        value += reverse_digits(value)
        trace.append(value)
    return trace


def is_palindrome(value: int) -> int:
    text = str(value)
    return int(text == text[::-1])


class ReverseAddTask(BaseMathTask):
    TASK_TYPE = "reverse_add"
    TASK_TYPES = ["value", "pal"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        digits = 2 if self.n <= 4 else 3
        low = 10 ** (digits - 1)
        high = 10 ** digits - 1
        self.start = random.randint(low, high)
        if is_palindrome(self.start):
            self.start = low
        self.trace = reverse_add_trace(self.start, self.n)
        self.value = self.trace[-1]
        self.pal = is_palindrome(self.value)
        self.answer = self.value if self.task_type == "value" else self.pal
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
