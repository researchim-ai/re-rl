"""FreeFallTask — падение из покоя при g = 10.

h = g * t^2 / 2 = 5 * t^2. Время — положительное целое, поэтому высота тоже целая.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fall_height(time: int, gravity: int = 10) -> int:
    return gravity * time * time // 2


class FreeFallTask(BaseMathTask):
    TASK_TYPE = "free_fall"
    TASK_TYPES = ["height", "time"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"t": 4}, 2: {"t": 6}, 3: {"t": 6}, 4: {"t": 8}, 5: {"t": 10},
        6: {"t": 12}, 7: {"t": 14}, 8: {"t": 16}, 9: {"t": 20}, 10: {"t": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.time = random.randint(1, int(p["t"]))
        self.height = fall_height(self.time)
        self.answer = self.height if self.task_type == "height" else self.time
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        law = (("Тело падает из покоя без сопротивления, g = 10. "
                "Высота h = g * t^2 / 2, время t — положительное целое.") if ru else
               ("A body falls from rest without drag, g = 10. "
                "The height is h = g * t^2 / 2, and the time t is a positive integer."))
        if self.task_type == "height":
            ask = ((f"t = {self.time}. Найдите h.") if ru else
                   (f"t = {self.time}. Find h."))
        else:
            ask = ((f"h = {self.height}. Найдите t.") if ru else
                   (f"h = {self.height}. Find t."))
        return f"{law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"h = 5 * {self.time}^2 = {self.height}.") if ru else
                (f"h = 5 * {self.time}^2 = {self.height}."))
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
