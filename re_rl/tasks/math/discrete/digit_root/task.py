"""DigitRootTask — повторная сумма цифр до одной цифры.

Сначала складываются цифры исходного числа, затем сумма цифр результата.
Число цифр растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def digit_sum(value: int) -> int:
    total = 0
    while value:
        total += value % 10
        value //= 10
    return total


def digit_trace(digits: Sequence[int]) -> Tuple[List[int], List[Tuple[int, int]], int, int]:
    running = []
    total = 0
    number = 0
    for digit in digits:
        total += digit
        number = number * 10 + digit
        running.append(total)
    folds = []
    value = number
    while value >= 10:
        nxt = digit_sum(value)
        folds.append((value, nxt))
        value = nxt
    return running, folds, value, len(folds)


class DigitRootTask(BaseMathTask):
    TASK_TYPE = "digit_root"
    TASK_TYPES = ["root", "rounds"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.digits = [random.randint(1, 9) for _ in range(self.n)]
        self.running, self.rounds, self.root, self.round_count = digit_trace(self.digits)
        self.answer = self.root if self.task_type == "root" else self.round_count
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "".join(str(digit) for digit in self.digits)
        key = "s0" if self.task_type == "root" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, digit=digit, total=total)
            for index, (digit, total) in enumerate(zip(self.digits, self.running), 1)
        ]
        for index, (before, after) in enumerate(self.rounds, 1):
            steps.append(texts.t("s3", self.language, i=index, before=before, after=after))
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
