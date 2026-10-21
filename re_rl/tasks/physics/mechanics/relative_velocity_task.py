"""RelativeVelocityTask — скорость одного тела относительно другого на прямой.

Положительное направление — вправо. Скорость A относительно B равна vA - vB.

Подтипы: относительная скорость и восстановление vA по относительной и vB.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RelativeVelocityTask(BaseMathTask):
    TASK_TYPE = "relative_velocity"
    TASK_TYPES = ["relative", "first_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 6}, 2: {"v": 8}, 3: {"v": 10}, 4: {"v": 12}, 5: {"v": 12},
        6: {"v": 15}, 7: {"v": 18}, 8: {"v": 20}, 9: {"v": 24}, 10: {"v": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["v"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.va = random.randint(-limit, limit)
        self.vb = random.randint(-limit, limit)
        self.relative = self.va - self.vb
        self.answer = self.relative if self.task_type == "relative" else self.va
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Прямая, вправо положительно. Скорость A относительно B равна vA - vB.") if ru else
                ("A straight line, right is positive. The velocity of A relative to B is vA - vB."))
        if self.task_type == "relative":
            ask = ((f"vA = {self.va} м/с, vB = {self.vb} м/с. Найдите скорость A относительно B.") if ru else
                   (f"vA = {self.va} m/s, vB = {self.vb} m/s. Find the velocity of A relative to B."))
        else:
            ask = ((f"Скорость A относительно B равна {self.relative} м/с, vB = {self.vb} м/с. Найдите vA.")
                   if ru else
                   (f"The velocity of A relative to B is {self.relative} m/s, vB = {self.vb} m/s. Find vA."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"vA - vB = {self.va} - ({self.vb}) = {self.relative}.") if ru else
                (f"vA - vB = {self.va} - ({self.vb}) = {self.relative}."))
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
