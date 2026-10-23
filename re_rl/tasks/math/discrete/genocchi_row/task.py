"""GenocchiRowTask — числа Генокки через числа Бернулли.

Сначала считается B(n) той же рекурсией. Затем G(n) = 2*(1-2^n)*B(n), и это целое.
Индекс чётный и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.discrete.bernoulli_numer.task import bernoulli_trace
from re_rl.tasks.math.logic import _logic_utils as U


def genocchi_value(order: int) -> int:
    numer, denom = bernoulli_trace(order)[0][-1]
    factor = 2 * (1 - 2 ** order)
    value = factor * numer
    assert value % denom == 0
    return value // denom


class GenocchiRowTask(BaseMathTask):
    TASK_TYPE = "genocchi_row"
    TASK_TYPES = ["value", "numer"]

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
        self.factor = 2 * (1 - 2 ** self.n)
        self.value = self.factor * self.numer // self.denom
        assert self.value == int(sp.genocchi(self.n))
        self.answer = self.value if self.task_type == "value" else self.numer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [texts.t("s2", self.language, numer=1, denom=1)]
        for m, k, coefficient, term_n, term_d, sum_n, sum_d in self.terms:
            steps.append(texts.t(
                "s3", self.language, m=m, k=k, upper=m + 1, coefficient=coefficient,
                term_n=term_n, term_d=term_d, sum_n=sum_n, sum_d=sum_d,
            ))
            if k == m - 1:
                numer, denom = self.values[m]
                steps.append(texts.t("s4", self.language, m=m, numer=numer, denom=denom))
        steps.append(texts.t(
            "s5", self.language, n=self.n, factor=self.factor,
            numer=self.numer, denom=self.denom, value=self.value,
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
