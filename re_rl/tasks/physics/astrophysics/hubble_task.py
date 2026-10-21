"""HubbleTask — закон Хаббла в выбранных единицах.

v = H * d. Две величины задаются, третья получается умножением или делением нацело.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hubble_speed(constant: int, distance: int) -> int:
    return constant * distance


class HubbleTask(BaseMathTask):
    TASK_TYPE = "hubble_law"
    TASK_TYPES = ["velocity", "distance", "constant"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 6}, 2: {"m": 8}, 3: {"m": 8}, 4: {"m": 10}, 5: {"m": 12},
        6: {"m": 12}, 7: {"m": 16}, 8: {"m": 18}, 9: {"m": 20}, 10: {"m": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.constant = random.randint(1, limit)
        self.distance = random.randint(1, limit)
        self.velocity = hubble_speed(self.constant, self.distance)
        self.answer = {
            "velocity": self.velocity,
            "distance": self.distance,
            "constant": self.constant,
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        law = ("В выбранных единицах закон Хаббла: v = H * d." if ru else
               "In the chosen units Hubble's law is v = H * d.")
        if self.task_type == "velocity":
            ask = ((f"H = {self.constant}, d = {self.distance}. Найдите скорость v.") if ru else
                   (f"H = {self.constant}, d = {self.distance}. Find the speed v."))
        elif self.task_type == "distance":
            ask = ((f"v = {self.velocity}, H = {self.constant}. Найдите расстояние d.") if ru else
                   (f"v = {self.velocity}, H = {self.constant}. Find the distance d."))
        else:
            ask = ((f"v = {self.velocity}, d = {self.distance}. Найдите постоянную H.") if ru else
                   (f"v = {self.velocity}, d = {self.distance}. Find the constant H."))
        return f"{law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"v = {self.constant} * {self.distance} = {self.velocity}.") if ru else
                (f"v = {self.constant} * {self.distance} = {self.velocity}."))
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
