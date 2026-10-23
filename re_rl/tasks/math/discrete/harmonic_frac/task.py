"""HarmonicFracTask — числитель гармонического числа.

H(n) — сумма 1/1 + 1/2 + ... + 1/n, сокращённая после каждого сложения.
Число слагаемых растёт с уровнем.
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


def harmonic_trace(order: int) -> List[Tuple[int, int]]:
    numer, denom = 0, 1
    trace = []
    for k in range(1, order + 1):
        numer, denom = reduce_frac(numer * k + denom, denom * k)
        trace.append((numer, denom))
    return trace


class HarmonicFracTask(BaseMathTask):
    TASK_TYPE = "harmonic_frac"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 9}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = harmonic_trace(self.n)
        self.numer, self.denom = self.trace[-1]
        library = sp.harmonic(self.n).as_numer_denom()
        assert (self.numer, self.denom) == (int(library[0]), int(library[1]))
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, numer=numer, denom=denom)
            for index, (numer, denom) in enumerate(self.trace, 1)
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
