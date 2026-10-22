"""MirrorGlanceTask — угол отражения от плоского зеркала.

Угол падения отсчитывается от нормали и не превосходит 89°, поэтому оба ответа положительны.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class MirrorGlanceTask(BaseMathTask):
    TASK_TYPE = "mirror_glance"
    TASK_TYPES = ["glance", "deviation"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 20}, 2: {"a": 30}, 3: {"a": 40}, 4: {"a": 45}, 5: {"a": 50},
        6: {"a": 60}, 7: {"a": 70}, 8: {"a": 75}, 9: {"a": 80}, 10: {"a": 85},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.angle = random.randint(1, int(p["a"]))
        self.glance = 90 - self.angle
        self.deviation = 180 - 2 * self.angle
        self.answer = self.glance if self.task_type == "glance" else self.deviation
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "glance" else "s1"
        return texts.t(key, language, angle=self.angle)

    def solve(self):
        if self.task_type == "glance":
            step = texts.t("s2", self.language, angle=self.angle, answer=self.glance)
        else:
            step = texts.t("s3", self.language, angle=self.angle, answer=self.deviation)
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
