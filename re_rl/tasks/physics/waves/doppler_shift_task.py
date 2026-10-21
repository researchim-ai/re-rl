"""DopplerShiftTask — целочисленный сдвиг частоты звука.

Наблюдатель и источник сближаются: f' = f * (c + vo) / (c - vs), vs < c.
Числа подобраны так, что деление проходит нацело.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def doppler_observed(frequency: int, sound: int, source: int, observer: int) -> int:
    value = Fraction(frequency * (sound + observer), sound - source)
    if value.denominator != 1:
        raise ValueError("частота не целая")
    return int(value)


class DopplerShiftTask(BaseMathTask):
    TASK_TYPE = "doppler_shift"
    TASK_TYPES = ["observed", "source_speed", "observer_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"c": 8, "k": 2}, 2: {"c": 10, "k": 3}, 3: {"c": 12, "k": 3},
        4: {"c": 14, "k": 4}, 5: {"c": 16, "k": 4}, 6: {"c": 18, "k": 5},
        7: {"c": 20, "k": 5}, 8: {"c": 24, "k": 6}, 9: {"c": 28, "k": 6},
        10: {"c": 32, "k": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        limit = int(p["c"])
        self.sound = random.randint(2, limit)
        self.source = random.randint(0, self.sound - 1)
        self.observer = random.randint(0, limit)
        self.factor = random.randint(1, int(p["k"]))
        self.frequency = self.factor * (self.sound - self.source)
        self.observed = doppler_observed(self.frequency, self.sound, self.source, self.observer)
        self.answer = {
            "observed": self.observed,
            "source_speed": self.source,
            "observer_speed": self.observer,
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        law = (("Источник и наблюдатель сближаются. f' = f * (c + vo) / (c - vs), "
                "скорость звука c, источник медленнее звука.") if ru else
               ("The source and the observer move toward each other. f' = f * (c + vo) / (c - vs), "
                "c is the speed of sound, and the source is slower than sound."))
        if self.task_type == "observed":
            ask = ((f"f = {self.frequency}, c = {self.sound}, vs = {self.source}, vo = {self.observer}. Найдите f'.")
                   if ru else
                   (f"f = {self.frequency}, c = {self.sound}, vs = {self.source}, vo = {self.observer}. Find f'."))
        elif self.task_type == "source_speed":
            ask = ((f"f = {self.frequency}, f' = {self.observed}, c = {self.sound}, vo = {self.observer}. Найдите vs.")
                   if ru else
                   (f"f = {self.frequency}, f' = {self.observed}, c = {self.sound}, vo = {self.observer}. Find vs."))
        else:
            ask = ((f"f = {self.frequency}, f' = {self.observed}, c = {self.sound}, vs = {self.source}. Найдите vo.")
                   if ru else
                   (f"f = {self.frequency}, f' = {self.observed}, c = {self.sound}, vs = {self.source}. Find vo."))
        return f"{law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"f' = {self.frequency} * ({self.sound} + {self.observer}) / ({self.sound} - {self.source}) "
                 f"= {self.observed}.") if ru else
                (f"f' = {self.frequency} * ({self.sound} + {self.observer}) / ({self.sound} - {self.source}) "
                 f"= {self.observed}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
