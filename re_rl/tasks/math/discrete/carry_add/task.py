"""CarryAddTask — сложение в столбик и число переносов.

Число разрядов растёт с уровнем. Сумму можно сложить сразу, число переносов — только пройдя разряды справа налево.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _to_int(digits: List[int]) -> int:
    value = 0
    for digit in reversed(digits):
        value = value * 10 + digit
    return value


class CarryAddTask(BaseMathTask):
    TASK_TYPE = "carry_add"
    TASK_TYPES = ["sum", "carries"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7}, 9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.a_digits = [random.randint(0, 9) for _ in range(self.n)]
        self.b_digits = [random.randint(0, 9) for _ in range(self.n)]
        self.a_digits[-1] = random.randint(1, 9)
        self.b_digits[-1] = random.randint(1, 9)
        self.a = _to_int(self.a_digits)
        self.b = _to_int(self.b_digits)
        carry = 0
        self.carries = 0
        result = []
        self.columns: List[Dict[str, int]] = []
        for index in range(self.n):
            total = self.a_digits[index] + self.b_digits[index] + carry
            digit = total % 10
            nxt = total // 10
            if nxt:
                self.carries += 1
            self.columns.append({
                "a": self.a_digits[index], "b": self.b_digits[index],
                "carry_in": carry, "total": total, "digit": digit, "carry_out": nxt,
            })
            result.append(digit)
            carry = nxt
        if carry:
            result.append(carry)
        self.sum = _to_int(result)
        self.answer = self.sum if self.task_type == "sum" else self.carries
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "sum" else "s1"
        return texts.t(key, language, a=self.a, b=self.b, n=self.n)

    def solve(self):
        steps = []
        for index, column in enumerate(self.columns, 1):
            steps.append(texts.t("s2", self.language, i=index, **column))
        steps.append(texts.t("s3", self.language, sum=self.sum, carries=self.carries))
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
