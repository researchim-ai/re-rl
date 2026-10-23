"""TernaryBalanceTask — груз на чашечных весах с гирями степеней тройки.

Каждая гиря стоит слева вместе с грузом, справа против него или остаётся в стороне.
Расклад единственный. Число гирь растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def place_weights(target: int, count: int) -> List[int]:
    digits = []
    value = target
    for _ in range(count):
        remainder = value % 3
        if remainder == 2:
            digits.append(-1)
            value += 1
        else:
            digits.append(remainder)
            value -= remainder
        value //= 3
    assert value == 0
    return digits


class TernaryBalanceTask(BaseMathTask):
    TASK_TYPE = "ternary_balance"
    TASK_TYPES = ["right", "used"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.weights = [3 ** index for index in range(self.n)]
        limit = (3 ** self.n - 1) // 2
        self.target = random.randint(1, limit)
        self.digits = place_weights(self.target, self.n)
        self.right = sum(weight for weight, digit in zip(self.weights, self.digits) if digit == 1)
        self.used = sum(1 for digit in self.digits if digit != 0)
        self.answer = self.right if self.task_type == "right" else self.used
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        weights = ", ".join(str(weight) for weight in self.weights)
        key = "s0" if self.task_type == "right" else "s1"
        return texts.t(key, language, n=self.n, weights=weights, target=self.target)

    def solve(self):
        value = self.target
        steps = []
        for weight, digit in zip(self.weights, self.digits):
            remainder = value % 3
            steps.append(texts.t(
                "s2", self.language, weight=weight, remainder=remainder, place=digit, left=value,
            ))
            if digit == -1:
                value += 1
            elif digit == 1:
                value -= 1
            value //= 3
        steps.append(texts.t("s3", self.language, right=self.right, used=self.used))
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
