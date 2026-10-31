"""VTraceTask — один шаг V-trace.

ρ = min(ρ̄, π/μ).
Цель = V + ρ * (r + γ * V' - V).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_BARS = [Fraction(1, 1), Fraction(2, 1), Fraction(1, 2)]


def vtrace_step(ratio: Fraction, rho_bar: Fraction, reward: int, gamma: Fraction,
                value: int, nxt: int) -> Tuple[Fraction, Fraction]:
    rho = min(ratio, rho_bar)
    return rho, value + rho * (reward + gamma * nxt - value)


class VTraceTask(BaseMathTask):
    TASK_TYPE = "vtrace"
    TASK_TYPES = ["rho", "target"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mag": 4}, 2: {"mag": 5}, 3: {"mag": 6}, 4: {"mag": 6}, 5: {"mag": 8},
        6: {"mag": 8}, 7: {"mag": 10}, 8: {"mag": 10}, 9: {"mag": 12}, 10: {"mag": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.ratio = Fraction(random.randint(1, self.mag), random.randint(1, self.mag))
        self.rho_bar = random.choice(_BARS[:1 + min(2, difficulty // 4)])
        self.reward = random.randint(0, self.mag)
        self.gamma = Fraction(1, 2) if difficulty >= 4 and random.random() < 0.7 else Fraction(1, 1)
        self.value = random.randint(0, self.mag)
        self.nxt = random.randint(0, self.mag)
        self.rho, self.target = vtrace_step(
            self.ratio, self.rho_bar, self.reward, self.gamma, self.value, self.nxt)
        self.answer = self.rho if self.task_type == "rho" else self.target
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language, v0=fmt_fraction(self.ratio), v1=fmt_fraction(self.rho_bar), reward=self.reward, v3=fmt_fraction(self.gamma), value=self.value, nxt=self.nxt)))
        ask = (((texts.t('s2', language))) if self.task_type == "rho" else
               ((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.rl.detailed_solvers import solve_detailed
        solve_detailed(self)

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
