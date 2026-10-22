"""FrobeniusCoinTask — суммы из монет двух взаимно простых достоинств.

Наибольшая непредставимая сумма равна ab − a − b.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def coin_pair(amount: int, a: int, b: int) -> Optional[Tuple[int, int]]:
    x = 0
    while a * x <= amount:
        rest = amount - a * x
        if rest % b == 0:
            return x, rest // b
        x += 1
    return None


def coprime_denominations(limit: int) -> Tuple[int, int]:
    upper = max(4, limit)
    for _ in range(40):
        a = random.randint(2, upper - 1)
        b = random.randint(a + 1, upper)
        if math.gcd(a, b) == 1:
            return a, b
    return 2, 3


class FrobeniusCoinTask(BaseMathTask):
    TASK_TYPE = "frobenius_coin"
    TASK_TYPES = ["largest", "possible"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 8}, 3: {"n": 9}, 4: {"n": 10}, 5: {"n": 12},
        6: {"n": 14}, 7: {"n": 16}, 8: {"n": 18}, 9: {"n": 20}, 10: {"n": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.a, self.b = coprime_denominations(int(p["n"]))
        self.largest = self.a * self.b - self.a - self.b
        if self.task_type == "largest":
            self.possible = False
            self.amount = self.largest
            self.pair = None
            self.answer = self.largest
        else:
            self.possible = random.choice([True, False])
            if self.possible:
                x = random.randint(0, self.b)
                y = random.randint(0, self.a)
                if x == 0 and y == 0:
                    x = 1
                self.amount = self.a * x + self.b * y
                self.pair = (x, y)
            else:
                blocked = [n for n in range(1, self.largest + 1) if coin_pair(n, self.a, self.b) is None]
                self.amount = random.choice(blocked)
                self.pair = None
            self.answer = self.possible
        self.language = language
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _word(self, language, truth: bool) -> str:
        return texts.t("s5" if truth else "s6", language)

    def _descr(self, language):
        if self.task_type == "largest":
            return texts.t("s0", language, a=self.a, b=self.b)
        return texts.t("s1", language, amount=self.amount, a=self.a, b=self.b)

    def solve(self):
        if self.task_type == "largest":
            step = texts.t("s2", self.language, a=self.a, b=self.b, largest=self.largest)
            shown = str(self.largest)
        elif self.pair is not None:
            x, y = self.pair
            step = texts.t("s3", self.language, x=x, a=self.a, y=y, b=self.b, amount=self.amount)
            shown = self._word(self.language, True)
        else:
            step = texts.t("s4", self.language, amount=self.amount, a=self.a, b=self.b)
            shown = self._word(self.language, False)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=shown)]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "possible":
            return U.verify_bool(prediction, self.possible)
        return U.verify_int(prediction, self.largest)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
