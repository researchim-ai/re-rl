"""FubiniRowTask — упорядоченные числа Белла.

F(0) = 1. Дальше F(n) — сумма C(n, k)*F(k) по k от 0 до n-1.
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from sympy.functions.combinatorial.numbers import stirling

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def fubini_trace(order: int) -> Tuple[List[int], List[Tuple[int, int, int, int, int, int]]]:
    values = [1]
    terms = []
    for n in range(1, order + 1):
        running = 0
        for k in range(n):
            coefficient = binom(n, k)
            term = coefficient * values[k]
            running += term
            terms.append((n, k, coefficient, values[k], term, running))
        values.append(running)
    return values, terms


def fubini_oracle(order: int) -> int:
    total = 0
    for k in range(order + 1):
        total += math.factorial(k) * int(stirling(order, k, kind=2))
    return total


class FubiniRowTask(BaseMathTask):
    TASK_TYPE = "fubini_row"
    TASK_TYPES = ["value", "term"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values, self.terms = fubini_trace(self.n)
        self.k = random.randint(0, self.n - 1)
        self.value = self.values[-1]
        self.term = next(item[4] for item in self.terms if item[0] == self.n and item[1] == self.k)
        assert self.value == fubini_oracle(self.n)
        self.answer = self.value if self.task_type == "value" else self.term
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [texts.t("s2", self.language, value=self.values[0])]
        for n, k, coefficient, earlier, term, running in self.terms:
            steps.append(texts.t(
                "s3", self.language, n=n, k=k, coefficient=coefficient,
                earlier=earlier, term=term, running=running,
            ))
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
