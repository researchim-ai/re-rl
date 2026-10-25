"""PopcountSumTask — сумма чисел единиц в двоичной записи.

Для каждого числа от 1 до n считается, сколько в нём единиц, и эти количества складываются.
Верхняя граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def popcount(number: int) -> int:
    count = 0
    while number:
        count += number & 1
        number >>= 1
    return count


def pop_trace(limit: int) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for number in range(1, limit + 1):
        bits = popcount(number)
        total += bits
        trace.append((bits, total))
    return trace


class PopcountSumTask(BaseMathTask):
    TASK_TYPE = "popcount_sum"
    TASK_TYPES = ["total", "bits"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = pop_trace(self.n)
        self.k = random.randint(1, self.n)
        self.bits = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.bits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bits=bits, total=total)
            for index, (bits, total) in enumerate(self.trace, 1)
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
