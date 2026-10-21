"""PendulumRatioTask — математический маятник без корня и без π в ответе.

Из T = 2π * sqrt(L/g) следует (T / 2π)^2 = L/g.
Спрашивается эта дробь либо длина при известном g.

Подтипы: ``ratio`` и ``length``.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class PendulumRatioTask(BaseMathTask):
    TASK_TYPE = "pendulum_ratio"
    TASK_TYPES = ["ratio", "length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 6}, 2: {"m": 8}, 3: {"m": 8}, 4: {"m": 10}, 5: {"m": 12},
        6: {"m": 12}, 7: {"m": 15}, 8: {"m": 16}, 9: {"m": 20}, 10: {"m": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.length = random.randint(1, limit)
        self.gravity = random.randint(1, limit)
        self.ratio = Fraction(self.length, self.gravity)
        self.answer = self.ratio if self.task_type == "ratio" else Fraction(self.length)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Для математического маятника (T / 2π)^2 = L/g. "
                 "Ответ — целое или несократимая дробь.") if ru else
                ("For a simple pendulum, (T / 2π)^2 = L/g. "
                 "Answer with an integer or a reduced fraction."))
        if self.task_type == "ratio":
            ask = ((f"Длина L = {self.length}, g = {self.gravity}. Найдите L/g.") if ru else
                   (f"Length L = {self.length}, g = {self.gravity}. Find L/g."))
        else:
            ask = ((f"g = {self.gravity}, L/g = {fmt_fraction(self.ratio)}. Найдите L.") if ru else
                   (f"g = {self.gravity}, L/g = {fmt_fraction(self.ratio)}. Find L."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"L/g = {self.length}/{self.gravity} = {fmt_fraction(self.ratio)}.") if ru else
                (f"L/g = {self.length}/{self.gravity} = {fmt_fraction(self.ratio)}."))
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
