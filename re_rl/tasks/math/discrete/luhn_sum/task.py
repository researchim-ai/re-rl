"""LuhnSumTask — контрольная сумма Луна.

Справа налево удваивается каждая цифра, начиная с крайней правой.
Если удвоение больше 9, из него вычитается 9. Число цифр растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def luhn_trace(digits: Sequence[int]) -> Tuple[List[Tuple[int, int, int]], int, int]:
    total = 0
    rows = []
    for offset, digit in enumerate(reversed(digits)):
        value = digit * 2 if offset % 2 == 0 else digit
        if value > 9:
            value -= 9
        total += value
        rows.append((digit, value, total))
    check = (10 - (total % 10)) % 10
    return rows, total, check


class LuhnSumTask(BaseMathTask):
    TASK_TYPE = "luhn_sum"
    TASK_TYPES = ["total", "check"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 9}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.digits = [random.randint(0, 9) for _ in range(self.n)]
        self.digits[0] = random.randint(1, 9)
        self.rows, self.total, self.check = luhn_trace(self.digits)
        self.answer = self.total if self.task_type == "total" else self.check
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(digit) for digit in self.digits)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, digit=digit, value=value, total=total)
            for index, (digit, value, total) in enumerate(self.rows, 1)
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
