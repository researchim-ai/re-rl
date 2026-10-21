"""BallisticPendulumTask — баллистический маятник.

Неупругий удар: m v = (m + M) V.
Дальше подъём: V^2 = 2 g h, g = 10 м/с^2.

Числа подобраны так, что V и h целые: V кратно 10, тогда h = V^2 / 20 — целое,
а отношение (m + M) / m — целое, поэтому скорость пули тоже целая.
Массы заданы в граммах; в законе сохранения импульса важны только их отношения.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BallisticPendulumTask(BaseMathTask):
    TASK_TYPE = "ballistic_pendulum"
    TASK_TYPES = ["block_speed", "height", "bullet_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 3, "a": 1}, 2: {"s": 4, "a": 1}, 3: {"s": 5, "a": 2},
        4: {"s": 5, "a": 2}, 5: {"s": 6, "a": 2}, 6: {"s": 8, "a": 3},
        7: {"s": 8, "a": 3}, 8: {"s": 10, "a": 3}, 9: {"s": 10, "a": 4},
        10: {"s": 12, "a": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.s_max = int(p["s"])
        self.a_max = int(p["a"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # (m+M)/m = s >= 2, массы в граммах.
        self.s = random.randint(2, max(2, self.s_max))
        self.m = random.choice([10, 20, 25, 50])
        self.M = self.m * (self.s - 1)
        self.a = random.randint(1, max(1, self.a_max))
        self.V = 10 * self.a
        self.h = 5 * self.a * self.a  # V^2 / (2*10)
        self.v = self.V * self.s
        if self.m * self.v != self.V * (self.m + self.M):
            raise RuntimeError("импульс баллистического маятника не сошёлся")
        if self.V * self.V != 20 * self.h:
            raise RuntimeError("энергия баллистического маятника не сошлась")
        self.answer = {"block_speed": self.V, "height": self.h, "bullet_speed": self.v}[self.task_type]

    def _descr(self, language):
        ru = language == "ru"
        g = ("Примите g = 10 м/с^2. Массы даны в граммах, скорости — в м/с." if ru else
             "Take g = 10 m/s^2. Masses are in grams, speeds in m/s.")
        common = ((f"Пуля массой {self.m} г попадает в брусок маятника массой {self.M} г и застревает.")
                  if ru else
                  (f"A bullet of mass {self.m} g hits a pendulum block of mass {self.M} g and sticks."))
        if self.task_type == "block_speed":
            ask = ((f"Скорость пули до удара {self.v} м/с. Найдите скорость бруска с пулей сразу после удара.")
                   if ru else
                   (f"The bullet's speed before impact is {self.v} m/s. Find the speed of the block "
                    f"with the embedded bullet right after impact."))
        elif self.task_type == "height":
            ask = ((f"Скорость пули до удара {self.v} м/с. На какую высоту в метрах поднимется маятник?")
                   if ru else
                   (f"The bullet's speed before impact is {self.v} m/s. To what height, in meters, "
                    f"does the pendulum rise?"))
        else:
            ask = ((f"Маятник поднимается на {self.h} м. Какой была скорость пули до удара?") if ru else
                   (f"The pendulum rises {self.h} m. What was the bullet's speed before impact?"))
        return f"{common} {g} {ask}"

    def solve(self):
        ru = self.language == "ru"
        momentum = ((f"Сохранение импульса: {self.m} * {self.v} = ({self.m} + {self.M}) * V, "
                     f"V = {self.V} м/с.") if ru else
                    (f"Momentum: {self.m} * {self.v} = ({self.m} + {self.M}) * V, V = {self.V} m/s."))
        energy = ((f"Энергия подъёма: V^2 = 2 g h, h = {self.V}^2 / 20 = {self.h} м.") if ru else
                  (f"Rise energy: V^2 = 2 g h, h = {self.V}^2 / 20 = {self.h} m."))
        if self.task_type == "block_speed":
            steps = [momentum]
        elif self.task_type == "height":
            steps = [momentum, energy]
        else:
            steps = [energy, momentum]
        steps.append(f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
