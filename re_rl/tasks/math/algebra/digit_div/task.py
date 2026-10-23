"""DigitDivTask — деление столбиком по цифрам.

Остаток начинается с нуля. На каждой цифре он умножается на 10, затем берётся цифра частного.
Число цифр растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def divide_digits(digits: Sequence[int], divisor: int) -> Tuple[int, int, List[int]]:
    remainder = 0
    quot_digits = []
    for digit in digits:
        remainder = remainder * 10 + digit
        quot_digits.append(remainder // divisor)
        remainder %= divisor
    quotient = 0
    for digit in quot_digits:
        quotient = quotient * 10 + digit
    return quotient, remainder, quot_digits


class DigitDivTask(BaseMathTask):
    TASK_TYPE = "digit_div"
    TASK_TYPES = ["quotient", "remainder"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "d": 9}, 2: {"n": 2, "d": 9}, 3: {"n": 3, "d": 9},
        4: {"n": 4, "d": 12}, 5: {"n": 5, "d": 12}, 6: {"n": 6, "d": 15},
        7: {"n": 7, "d": 15}, 8: {"n": 8, "d": 20}, 9: {"n": 9, "d": 20},
        10: {"n": 10, "d": 25},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.divisor = random.randint(2, max(2, int(p["d"])))
        self.digits = [random.randint(0, 9) for _ in range(self.n)]
        self.digits[0] = random.randint(1, 9)
        self.quotient, self.remainder, self.quot_digits = divide_digits(self.digits, self.divisor)
        self.number = 0
        for digit in self.digits:
            self.number = self.number * 10 + digit
        self.answer = self.quotient if self.task_type == "quotient" else self.remainder
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(digit) for digit in self.digits)
        key = "s0" if self.task_type == "quotient" else "s1"
        return texts.t(key, language, number=self.number, n=self.n, listing=listing, divisor=self.divisor)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, digit=digit, quot=quot, rem=rem)
            for index, (digit, quot, rem) in enumerate(
                self._remainders(), 1
            )
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def _remainders(self):
        remainder = 0
        rows = []
        for digit, quot in zip(self.digits, self.quot_digits):
            remainder = remainder * 10 + digit
            remainder %= self.divisor
            rows.append((digit, quot, remainder))
        return rows

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
