"""LCOscillatorTask — частота колебаний контура LC без сопротивления.

ω^2 = 1 / (L*C). L и C — положительные целые в условных единицах, поэтому ω^2
и искомая индуктивность — точные дроби или целые.

Подтипы: ``omega_squared`` и ``inductance`` (L по известным ω^2 и C).
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class LCOscillatorTask(BaseMathTask):
    TASK_TYPE = "lc_oscillator"
    TASK_TYPES = ["omega_squared", "inductance"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 4}, 2: {"m": 5}, 3: {"m": 6}, 4: {"m": 6}, 5: {"m": 8},
        6: {"m": 8}, 7: {"m": 10}, 8: {"m": 10}, 9: {"m": 12}, 10: {"m": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.L = random.randint(1, int(p["m"]))
        self.C = random.randint(1, int(p["m"]))
        self.omega_sq = Fraction(1, self.L * self.C)
        self.answer = self.omega_sq if self.task_type == "omega_squared" else Fraction(self.L)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Идеальный контур LC: квадрат циклической частоты ω^2 = 1 / (L*C). "
                 "L и C даны в условных единицах. Ответ — целое или несократимая дробь.")
                if ru else
                ("Ideal LC circuit: the square of the angular frequency is ω^2 = 1 / (L*C). "
                 "L and C are in arbitrary units. Answer with an integer or a reduced fraction."))
        if self.task_type == "omega_squared":
            ask = ((f"L = {self.L}, C = {self.C}. Найдите ω^2.") if ru else
                   (f"L = {self.L}, C = {self.C}. Find ω^2."))
        else:
            ask = ((f"C = {self.C}, ω^2 = {fmt_fraction(self.omega_sq)}. Найдите L.") if ru else
                   (f"C = {self.C}, ω^2 = {fmt_fraction(self.omega_sq)}. Find L."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"ω^2 = 1 / ({self.L}*{self.C}) = {fmt_fraction(self.omega_sq)}, L = {self.L}.")
                if ru else
                (f"ω^2 = 1 / ({self.L}*{self.C}) = {fmt_fraction(self.omega_sq)}, L = {self.L}."))
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
