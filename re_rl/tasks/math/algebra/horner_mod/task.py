"""HornerModTask — схема Горнера и остаток по модулю.

Коэффициенты идут от старшей степени к свободному члену.
Число коэффициентов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def horner_trace(coeffs: Sequence[int], point: int, modulus: int) -> List[Tuple[int, int]]:
    plain = 0
    folded = 0
    trace = []
    for coeff in coeffs:
        plain = plain * point + coeff
        folded = plain % modulus
        trace.append((plain, folded))
    return trace


def horner_plain(coeffs: Sequence[int], point: int) -> int:
    value = sp.Poly(list(coeffs), sp.symbols("x")).subs(sp.symbols("x"), point)
    return int(value)


class HornerModTask(BaseMathTask):
    TASK_TYPE = "horner_mod"
    TASK_TYPES = ["folded", "plain"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.point = random.randint(2, 4)
        self.modulus = random.choice((5, 7, 11))
        self.coeffs = [random.randint(-3, 4) for _ in range(self.n)]
        if self.coeffs[0] == 0:
            self.coeffs[0] = 1
        self.trace = horner_trace(self.coeffs, self.point, self.modulus)
        self.plain, self.folded = self.trace[-1]
        assert self.plain == horner_plain(self.coeffs, self.point)
        self.answer = self.folded if self.task_type == "folded" else self.plain
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(coeff) for coeff in self.coeffs)
        key = "s0" if self.task_type == "folded" else "s1"
        return texts.t(
            key, language, n=self.n, point=self.point, modulus=self.modulus, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, plain=plain, folded=folded)
            for index, (plain, folded) in enumerate(self.trace, 1)
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
