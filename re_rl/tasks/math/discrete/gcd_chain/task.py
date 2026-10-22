"""GcdChainTask — последовательное вычисление НОД нескольких чисел.

Число аргументов растёт с уровнем. Все числа кратны одному множителю, поэтому НОД не случаен.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GcdChainTask(BaseMathTask):
    TASK_TYPE = "gcd_chain"
    TASK_TYPES = ["final"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 8}, 2: {"n": 2, "v": 12}, 3: {"n": 3, "v": 16},
        4: {"n": 3, "v": 20}, 5: {"n": 4, "v": 24}, 6: {"n": 5, "v": 30},
        7: {"n": 6, "v": 36}, 8: {"n": 7, "v": 42}, 9: {"n": 8, "v": 48},
        10: {"n": 10, "v": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "final"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(2, int(p["v"]))
        base = random.randint(1, max(1, limit // 2))
        span = max(1, limit // base)
        self.numbers: List[int] = [base * random.randint(1, span) for _ in range(self.n)]
        self.trace: List[int] = []
        current = 0
        for item in self.numbers:
            current = math.gcd(current, item)
            self.trace.append(current)
        self.answer = current
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.numbers)
        return texts.t("s0", language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        previous = 0
        for index, (number, value) in enumerate(zip(self.numbers, self.trace), 1):
            steps.append(texts.t("s1", self.language, i=index, prev=previous, number=number, value=value))
            previous = value
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
