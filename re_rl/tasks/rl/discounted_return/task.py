"""DiscountedReturnTask — дисконтированная отдача траектории.

G = r0 + γ r1 + ... + γ^{n-1} r_{n-1}, степени γ считаются дробями.
Подтипы:
- ``return``    — полная отдача без бутстрапа;
- ``n_step``    — n-шаговая отдача r0 + ... + γ^{n-1} r_{n-1} + γ^n V;
- ``advantage`` — полная отдача минус оценка V начального состояния.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_GAMMAS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


def discounted(rewards: List[int], gamma: Fraction, bootstrap: Optional[int] = None) -> Fraction:
    acc = Fraction(0)
    power = Fraction(1)
    for reward in rewards:
        acc += power * reward
        power *= gamma
    if bootstrap is not None:
        acc += power * bootstrap
    return acc


class DiscountedReturnTask(BaseMathTask):
    TASK_TYPE = "discounted_return"
    TASK_TYPES = ["return", "n_step", "advantage"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 3}, 2: {"n": 2, "mag": 4}, 3: {"n": 3, "mag": 4},
        4: {"n": 3, "mag": 5}, 5: {"n": 4, "mag": 5}, 6: {"n": 4, "mag": 6},
        7: {"n": 5, "mag": 6}, 8: {"n": 5, "mag": 6}, 9: {"n": 6, "mag": 7},
        10: {"n": 7, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.gamma = random.choice(_GAMMAS[:1 + min(3, difficulty // 3)])
        self.rewards = [random.randint(-self.mag, self.mag) for _ in range(self.count)]
        self.v_boot = random.randint(-self.mag, self.mag)
        self.v_start = random.randint(-self.mag, self.mag)
        if self.task_type == "n_step":
            self.answer = discounted(self.rewards, self.gamma, self.v_boot)
        elif self.task_type == "advantage":
            self.answer = discounted(self.rewards, self.gamma) - self.v_start
        else:
            self.answer = discounted(self.rewards, self.gamma)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rewards(self) -> str:
        return ", ".join(map(str, self.rewards))

    def _descr(self, language):
        gamma = fmt_fraction(self.gamma)
        rewards = self._rewards()
        rule = ((texts.t('s0', language, gamma=gamma)))
        if self.task_type == "n_step":
            ask = ((texts.t('s2', language, rewards=rewards, v_boot=self.v_boot)))
        elif self.task_type == "advantage":
            ask = ((texts.t('s3', language, rewards=rewards, v_start=self.v_start)))
        else:
            ask = ((texts.t('s4', language, rewards=rewards)))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        full = fmt_fraction(discounted(self.rewards, self.gamma))
        step = ((texts.t('s1', self.language, full=full, shown=shown)))
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
