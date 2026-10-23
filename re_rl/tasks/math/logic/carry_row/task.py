"""CarryRowTask — сложение в столбик и переносы.

Цифры идут от младшего разряда. Перенос — целая часть суммы цифр и прежнего переноса.
Число разрядов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def carry_trace(left: Sequence[int], right: Sequence[int]) -> Tuple[List[Tuple[int, int, int, int]], int, int]:
    carry = 0
    value = 0
    place = 1
    carries = 0
    trace = []
    for digit_a, digit_b in zip(left, right):
        total = digit_a + digit_b + carry
        digit = total % 10
        carry = total // 10
        if carry:
            carries += 1
        value += digit * place
        place *= 10
        trace.append((digit, carry, value, carries))
    value += carry * place
    return trace, value, carries


class CarryRowTask(BaseMathTask):
    TASK_TYPE = "carry_row"
    TASK_TYPES = ["sum", "carries"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.left = [random.randint(0, 9) for _ in range(self.n)]
        self.right = [random.randint(0, 9) for _ in range(self.n)]
        self.trace, self.sum, self.carries = carry_trace(self.left, self.right)
        self.answer = self.sum if self.task_type == "sum" else self.carries
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        left = ", ".join(str(digit) for digit in self.left)
        right = ", ".join(str(digit) for digit in self.right)
        key = "s0" if self.task_type == "sum" else "s1"
        return texts.t(key, language, n=self.n, left=left, right=right)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, digit=digit, carry=carry, value=value, carries=carries)
            for index, (digit, carry, value, carries) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, carry=self.trace[-1][1], value=self.sum))
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
