"""WaveRelationTask — связь скорости, частоты и длины волны.

v = f * λ. Два числа задаются, третье получается делением или умножением нацело.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def wave_speed(frequency: int, wavelength: int) -> int:
    return frequency * wavelength


class WaveRelationTask(BaseMathTask):
    TASK_TYPE = "wave_relation"
    TASK_TYPES = ["speed", "frequency", "wavelength"]

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
        self.frequency = random.randint(1, limit)
        self.wavelength = random.randint(1, limit)
        self.speed = wave_speed(self.frequency, self.wavelength)
        self.answer = {
            "speed": self.speed,
            "frequency": self.frequency,
            "wavelength": self.wavelength,
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        law = ("Для волны v = f * λ." if ru else "For a wave, v = f * λ.")
        if self.task_type == "speed":
            ask = ((f"Частота f = {self.frequency}, длина волны λ = {self.wavelength}. Найдите скорость v.")
                   if ru else
                   (f"Frequency f = {self.frequency}, wavelength λ = {self.wavelength}. Find the speed v."))
        elif self.task_type == "frequency":
            ask = ((f"Скорость v = {self.speed}, длина волны λ = {self.wavelength}. Найдите частоту f.")
                   if ru else
                   (f"Speed v = {self.speed}, wavelength λ = {self.wavelength}. Find the frequency f."))
        else:
            ask = ((f"Скорость v = {self.speed}, частота f = {self.frequency}. Найдите длину волны λ.")
                   if ru else
                   (f"Speed v = {self.speed}, frequency f = {self.frequency}. Find the wavelength λ."))
        return f"{law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"v = {self.frequency} * {self.wavelength} = {self.speed}.") if ru else
                (f"v = {self.frequency} * {self.wavelength} = {self.speed}."))
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
