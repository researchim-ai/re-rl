"""EchoDelayTask — расстояние до стены по времени эха.

Скорость звука 340 м/с, время целый число секунд, поэтому путь в одну сторону кратен 170 м.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

SOUND_SPEED = 340


class EchoDelayTask(BaseMathTask):
    TASK_TYPE = "echo_delay"
    TASK_TYPES = ["distance", "time"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"t": 4}, 2: {"t": 6}, 3: {"t": 8}, 4: {"t": 10}, 5: {"t": 12},
        6: {"t": 16}, 7: {"t": 20}, 8: {"t": 24}, 9: {"t": 30}, 10: {"t": 40},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.time = random.randint(1, int(p["t"]))
        self.distance = SOUND_SPEED * self.time // 2
        self.answer = self.distance if self.task_type == "distance" else self.time
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "distance":
            return texts.t("s0", language, time=self.time)
        return texts.t("s1", language, distance=self.distance)

    def solve(self):
        if self.task_type == "distance":
            step = texts.t("s2", self.language, time=self.time, distance=self.distance)
        else:
            step = texts.t("s3", self.language, distance=self.distance, time=self.time)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
