"""RationalGammaTask — фактор Лоренца, который сокращается до дроби.

v/c берётся из пифагоровой тройки, поэтому γ = 1/sqrt(1 - (v/c)^2) рационален.
Собственное время τ = t / γ, где t — лабораторное время.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

# (числитель v/c, знаменатель v/c, знаменатель γ): a^2 + k^2 = b^2, γ = b/k.
_TRIPLES: List[Tuple[int, int, int]] = [
    (3, 5, 4), (5, 13, 12), (8, 17, 15), (7, 25, 24), (20, 29, 21),
    (12, 37, 35), (9, 41, 40), (28, 53, 45), (11, 61, 60), (33, 65, 56),
    (16, 65, 63), (36, 85, 77), (39, 89, 80), (48, 73, 55), (65, 97, 72),
]


def lorentz_factor(numer: int, denom: int, gamma_den: int) -> Fraction:
    if numer * numer + gamma_den * gamma_den != denom * denom:
        raise ValueError(texts.literal('literals.s3'))
    return Fraction(denom, gamma_den)


def proper_time(lab_time: int, denom: int, gamma_den: int) -> Fraction:
    return Fraction(lab_time * gamma_den, denom)


class RationalGammaTask(BaseMathTask):
    TASK_TYPE = "rational_gamma"
    TASK_TYPES = ["gamma", "proper_time"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"triples": 2, "t": 6}, 2: {"triples": 3, "t": 8}, 3: {"triples": 4, "t": 8},
        4: {"triples": 5, "t": 10}, 5: {"triples": 6, "t": 12}, 6: {"triples": 8, "t": 12},
        7: {"triples": 10, "t": 16}, 8: {"triples": 12, "t": 16}, 9: {"triples": 14, "t": 20},
        10: {"triples": 15, "t": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        span = max(1, min(len(_TRIPLES), int(p["triples"])))
        self.numer, self.denom, self.gamma_den = random.choice(_TRIPLES[:span])
        self.lab_time = random.randint(1, int(p["t"]))
        self.gamma = lorentz_factor(self.numer, self.denom, self.gamma_den)
        self.tau = proper_time(self.lab_time, self.denom, self.gamma_den)
        self.answer = self.gamma if self.task_type == "gamma" else self.tau
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        speed = f"{self.numer}/{self.denom}"
        rule = ((texts.t('s0', language, speed=speed)))
        if self.task_type == "gamma":
            ask = ((texts.t('s1', language)))
        else:
            ask = ((texts.t('s2', language, lab_time=self.lab_time)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((f"γ = {fmt_fraction(self.gamma)}, τ = {fmt_fraction(self.tau)}."))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
