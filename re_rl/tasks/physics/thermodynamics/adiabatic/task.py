"""AdiabaticTask — обратимый адиабатический процесс идеального газа.

Объёмы выбираются степенями целого k, которые сокращаются с показателем
адиабаты, поэтому T2, P2 и V2 получаются целыми.

Одноатомный газ: γ = 5/3. Двухатомный: γ = 7/5.
T V^{γ−1} = const, P V^γ = const.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_GASES = {
    "monatomic": {"ru": texts.literal('literals.s6'), "en": "monatomic", "gamma": Fraction(5, 3)},
    "diatomic": {"ru": texts.literal('literals.s7'), "en": "diatomic", "gamma": Fraction(7, 5)},
}


class AdiabaticTask(BaseMathTask):
    TASK_TYPE = "adiabatic"
    TASK_TYPES = ["temperature", "pressure", "volume"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 2}, 2: {"k": 2}, 3: {"k": 2}, 4: {"k": 2}, 5: {"k": 2},
        6: {"k": 2}, 7: {"k": 2}, 8: {"k": 2}, 9: {"k": 2}, 10: {"k": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # Двухатомный газ даёт объёмный множитель 2^5 = 32 и давление ×128 — ещё точно.
        self.gas = "monatomic" if self.difficulty < 7 or random.random() < 0.5 else "diatomic"
        self.gamma: Fraction = _GASES[self.gas]["gamma"]
        self.k = 2
        self.expand = random.choice([True, False])
        gm1 = self.gamma - 1
        self.p_t, self.q_t = gm1.numerator, gm1.denominator
        self.p_p, self.q_p = self.gamma.numerator, self.gamma.denominator
        base = random.randint(1, 4)
        small = random.randint(2, 12) * 10  # удобное «маленькое» T или P
        vol_factor = self.k ** (self.q_t if self.task_type != "pressure" else self.q_p)
        temp_factor = self.k ** self.p_t
        pres_factor = self.k ** self.p_p
        if self.expand:
            self.V1 = base
            self.V2 = base * (self.k ** self.q_t)
            self.T2 = small
            self.T1 = small * temp_factor
            self.P2 = small
            self.P1 = small * pres_factor
        else:
            self.V2 = base
            self.V1 = base * (self.k ** self.q_t)
            self.T1 = small
            self.T2 = small * temp_factor
            self.P1 = small
            self.P2 = small * pres_factor
        # Для подтипа pressure объёмный множитель берётся по знаменателю γ, не γ−1.
        if self.task_type == "pressure":
            if self.expand:
                self.V1 = base
                self.V2 = base * vol_factor
            else:
                self.V2 = base
                self.V1 = base * vol_factor
        self._check()
        self.answer = {"temperature": self.T2, "pressure": self.P2, "volume": self.V2}[self.task_type]

    def _check(self):
        factor_t = self.k ** self.q_t
        factor_p = self.k ** self.q_p
        if self.task_type == "pressure":
            if self.expand:
                if self.V2 != self.V1 * factor_p or self.P1 != self.P2 * (self.k ** self.p_p):
                    raise RuntimeError(texts.t('s8', self.language))
            elif self.V1 != self.V2 * factor_p or self.P2 != self.P1 * (self.k ** self.p_p):
                raise RuntimeError(texts.t('s9', self.language))
        else:
            if self.expand:
                if self.V2 != self.V1 * factor_t or self.T1 != self.T2 * (self.k ** self.p_t):
                    raise RuntimeError(texts.t('s10', self.language))
            elif self.V1 != self.V2 * factor_t or self.T2 != self.T1 * (self.k ** self.p_t):
                raise RuntimeError(texts.t('s11', self.language))

    def _gamma_str(self) -> str:
        return f"{self.gamma.numerator}/{self.gamma.denominator}"

    def _descr(self, language):
        gas = _GASES[self.gas][(texts.t('s1', language))]
        gamma = self._gamma_str()
        head = ((texts.t('s0', language, gas=gas, gamma=gamma)))
        if self.task_type == "temperature":
            ask = ((texts.t('s2', language, V1=self.V1, V2=self.V2, T1=self.T1)))
        elif self.task_type == "pressure":
            ask = ((texts.t('s3', language, V1=self.V1, V2=self.V2, P1=self.P1)))
        else:
            ask = ((texts.t('s4', language, T1=self.T1, T2=self.T2, V1=self.V1)))
        return f"{head} {ask}"

    def solve(self):
        if self.task_type == "temperature":
            power = self.k ** self.p_t
            if self.expand:
                step = (({"ru": (f'V1/V2 = {self.V1}/{self.V2} = 1/{self.k}^{self.q_t}. (V1/V2)^(γ−1) = 1/{self.k}^{self.p_t} = 1/{power}. T2 = {self.T1} / {power} = {self.T2}.'), "en": (f'V1/V2 = {self.V1}/{self.V2} = 1/{self.k}^{self.q_t}. (V1/V2)^(γ−1) = 1/{power}. T2 = {self.T1} / {power} = {self.T2}.')}.get(self.language, (f'V1/V2 = {self.V1}/{self.V2} = 1/{self.k}^{self.q_t}. (V1/V2)^(γ−1) = 1/{power}. T2 = {self.T1} / {power} = {self.T2}.'))))
            else:
                step = (({"ru": (f'V1/V2 = {self.V1}/{self.V2} = {self.k}^{self.q_t}. (V1/V2)^(γ−1) = {self.k}^{self.p_t} = {power}. T2 = {self.T1} * {power} = {self.T2}.'), "en": (f'V1/V2 = {self.V1}/{self.V2} = {self.k}^{self.q_t}. (V1/V2)^(γ−1) = {power}. T2 = {self.T1} * {power} = {self.T2}.')}.get(self.language, (f'V1/V2 = {self.V1}/{self.V2} = {self.k}^{self.q_t}. (V1/V2)^(γ−1) = {power}. T2 = {self.T1} * {power} = {self.T2}.'))))
        elif self.task_type == "pressure":
            power = self.k ** self.p_p
            if self.expand:
                step = ((f"V1/V2 = {self.V1}/{self.V2} = 1/{self.k}^{self.q_p}. "
                         f"(V1/V2)^γ = 1/{power}. P2 = {self.P1} / {power} = {self.P2}."))
            else:
                step = ((f"V1/V2 = {self.V1}/{self.V2} = {self.k}^{self.q_p}. "
                         f"(V1/V2)^γ = {power}. P2 = {self.P1} * {power} = {self.P2}."))
        else:
            power = self.k ** self.q_t
            if self.expand:
                step = (({"ru": (texts.t('s13', self.language, T2=self.T2, T1=self.T1, k=self.k, p_t=self.p_t, k_2=self.k, q_t=self.q_t, power=power, V1=self.V1, power_2=power, V2=self.V2)), "en": (texts.t('s14', self.language, T2=self.T2, T1=self.T1, k=self.k, p_t=self.p_t, power=power, V1=self.V1, power_2=power, V2=self.V2))}.get(self.language, (texts.t('s12', self.language, T2=self.T2, T1=self.T1, k=self.k, p_t=self.p_t, power=power, V1=self.V1, power_2=power, V2=self.V2)))))
            else:
                step = ((texts.t('s5', self.language, T2=self.T2, T1=self.T1, k=self.k, p_t=self.p_t, power=power, V1=self.V1, power_2=power, V2=self.V2)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
