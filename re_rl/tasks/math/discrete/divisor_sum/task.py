"""DivisorSumTask — число и сумма положительных делителей.

Перебор идёт до корня, поэтому ответ точный для любого целого n ≥ 2.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def positive_divisors(n: int) -> List[int]:
    small = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            small.append(i)
        i += 1
    large = [n // item for item in small if n // item != item]
    return small + large[::-1]


class DivisorSumTask(BaseMathTask):
    TASK_TYPE = "divisor_sum"
    TASK_TYPES = ["count", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 20}, 2: {"n": 30}, 3: {"n": 40}, 4: {"n": 60}, 5: {"n": 80},
        6: {"n": 100}, 7: {"n": 150}, 8: {"n": 200}, 9: {"n": 300}, 10: {"n": 400},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = random.randint(2, int(p["n"]))
        self.divisors = positive_divisors(self.n)
        self.count = len(self.divisors)
        self.total = sum(self.divisors)
        self.answer = self.count if self.task_type == "count" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        shown = ", ".join(str(item) for item in self.divisors)
        step = texts.t("s2", self.language, divs=shown, count=self.count, total=self.total)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
