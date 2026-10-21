"""GaeTask — обобщённое преимущество GAE(λ).

δ_i = r_i + γ V_(i+1) - V_i.
A_t = δ_t + (γλ) δ_(t+1) + (γλ)^2 δ_(t+2) + ... до конца траектории.
Последнее V — бутстрап после финальной награды. Шаги нумеруются с 0.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_FACTORS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


def td_delta(rewards: List[int], values: List[int], gamma: Fraction, t: int) -> Fraction:
    return Fraction(rewards[t]) + gamma * values[t + 1] - values[t]


def gae_advantage(rewards: List[int], values: List[int], gamma: Fraction, lam: Fraction, t: int) -> Fraction:
    factor = gamma * lam
    acc = Fraction(0)
    for i in range(len(rewards) - 1, t - 1, -1):
        acc = td_delta(rewards, values, gamma, i) + factor * acc
    return acc


class GaeTask(BaseMathTask):
    TASK_TYPE = "gae_advantage"
    TASK_TYPES = ["advantage", "delta"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 3}, 2: {"n": 2, "mag": 4}, 3: {"n": 3, "mag": 4},
        4: {"n": 3, "mag": 5}, 5: {"n": 3, "mag": 6}, 6: {"n": 4, "mag": 6},
        7: {"n": 4, "mag": 7}, 8: {"n": 5, "mag": 7}, 9: {"n": 5, "mag": 8},
        10: {"n": 6, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        span = _FACTORS[:1 + min(3, difficulty // 3)]
        self.gamma = random.choice(span)
        self.lam = random.choice(span)
        self.rewards = [random.randint(0, self.mag) for _ in range(self.count)]
        self.values = [random.randint(0, self.mag) for _ in range(self.count + 1)]
        self.t = random.randrange(self.count)
        self.delta = td_delta(self.rewards, self.values, self.gamma, self.t)
        self.advantage = gae_advantage(self.rewards, self.values, self.gamma, self.lam, self.t)
        self.answer = self.advantage if self.task_type == "advantage" else self.delta
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rewards = ", ".join(map(str, self.rewards))
        values = ", ".join(map(str, self.values))
        rule = ((f"GAE. δ_i = r_i + γ * V_(i+1) - V_i. "
                 f"Преимущество A_t — сумма δ_i с шага t до конца, каждый следующий δ умножается на γλ. "
                 f"Оценок V на одну больше, чем наград: последняя — бутстрап. Шаги с 0. "
                 f"γ = {fmt_fraction(self.gamma)}, λ = {fmt_fraction(self.lam)}. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"GAE. δ_i = r_i + γ * V_(i+1) - V_i. "
                 f"Advantage A_t sums δ_i from step t to the end; each later δ is multiplied by γλ. "
                 f"There is one more V than rewards: the last is the bootstrap. Steps start at 0. "
                 f"γ = {fmt_fraction(self.gamma)}, λ = {fmt_fraction(self.lam)}. "
                 f"Answer with an integer or a reduced fraction."))
        data = ((f"Награды: {rewards}. Оценки V: {values}.") if ru else
                (f"Rewards: {rewards}. Values V: {values}."))
        if self.task_type == "advantage":
            ask = ((f"Найдите A_{self.t}.") if ru else (f"Find A_{self.t}."))
        else:
            ask = ((f"Найдите δ_{self.t}.") if ru else (f"Find δ_{self.t}."))
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"δ_{self.t} = {fmt_fraction(self.delta)}, A_{self.t} = {fmt_fraction(self.advantage)}.")
                if ru else
                (f"δ_{self.t} = {fmt_fraction(self.delta)}, A_{self.t} = {fmt_fraction(self.advantage)}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
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
