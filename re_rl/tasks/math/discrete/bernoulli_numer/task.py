"""BernoulliNumerTask — числитель числа Бернулли.

B(0) = 1. Дальше B(m) — это минус сумма C(m+1, k)*B(k), делённая на m+1.
Индекс чётный и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def reduce_frac(numer: int, denom: int) -> Tuple[int, int]:
    if denom < 0:
        numer, denom = -numer, -denom
    common = math.gcd(numer, denom)
    return numer // common, denom // common


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def bernoulli_trace(order: int):
    values = [(1, 1)]
    terms = []
    for m in range(1, order + 1):
        sum_n, sum_d = 0, 1
        for k in range(m):
            coefficient = binom(m + 1, k)
            term_n, term_d = reduce_frac(coefficient * values[k][0], values[k][1])
            sum_n, sum_d = reduce_frac(sum_n * term_d + term_n * sum_d, sum_d * term_d)
            terms.append((m, k, coefficient, term_n, term_d, sum_n, sum_d))
        values.append(reduce_frac(-sum_n, sum_d * (m + 1)))
    return values, terms


class BernoulliNumerTask(BaseMathTask):
    TASK_TYPE = "bernoulli_numer"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 4}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values, self.terms = bernoulli_trace(self.n)
        self.numer, self.denom = self.values[-1]
        library = sp.bernoulli(self.n).as_numer_denom()
        assert (self.numer, self.denom) == (int(library[0]), int(library[1]))
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [texts.t("s2", self.language, numer=1, denom=1)]
        shown = {0}
        for m, k, coefficient, term_n, term_d, sum_n, sum_d in self.terms:
            steps.append(texts.t(
                "s3", self.language, m=m, k=k, upper=m + 1, coefficient=coefficient,
                term_n=term_n, term_d=term_d, sum_n=sum_n, sum_d=sum_d,
            ))
            if k == m - 1 and m not in shown:
                numer, denom = self.values[m]
                steps.append(texts.t("s4", self.language, m=m, numer=numer, denom=denom))
                shown.add(m)
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
