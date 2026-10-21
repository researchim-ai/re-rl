"""WaveRelationTask — связь скорости, частоты и длины волны.

v = f * λ. Два числа задаются, третье получается делением или умножением нацело.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        law = ((texts.t('s0', language)))
        if self.task_type == "speed":
            ask = ((texts.t('s2', language, frequency=self.frequency, wavelength=self.wavelength)))
        elif self.task_type == "frequency":
            ask = ((texts.t('s3', language, speed=self.speed, wavelength=self.wavelength)))
        else:
            ask = ((texts.t('s4', language, speed=self.speed, frequency=self.frequency)))
        return f"{law} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, frequency=self.frequency, wavelength=self.wavelength, speed=self.speed)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
