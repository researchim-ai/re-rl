"""RestitutionTask — центральный удар о покоящееся тело.

Коэффициент восстановления e равен 0 или 1. Начальная скорость первого тела
кратна сумме масс, поэтому обе скорости после удара целые.
Положительное направление — начальное направление первого тела. Второе покоится.

Подтипы: скорость первого и скорость второго после удара.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RestitutionTask(BaseMathTask):
    TASK_TYPE = "restitution"
    TASK_TYPES = ["first_speed", "second_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 3, "t": 2}, 2: {"m": 4, "t": 2}, 3: {"m": 4, "t": 3},
        4: {"m": 5, "t": 3}, 5: {"m": 5, "t": 3}, 6: {"m": 6, "t": 4},
        7: {"m": 7, "t": 4}, 8: {"m": 8, "t": 4}, 9: {"m": 9, "t": 5},
        10: {"m": 10, "t": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.e = random.choice([0, 1])
        self.m1 = random.randint(1, int(p["m"]))
        self.m2 = random.randint(1, int(p["m"]))
        self.t = random.randint(1, int(p["t"]))
        self.u = (self.m1 + self.m2) * self.t
        self.v1 = (self.m1 - self.e * self.m2) * self.t
        self.v2 = self.m1 * (1 + self.e) * self.t
        if self.m1 * self.u != self.m1 * self.v1 + self.m2 * self.v2:
            raise RuntimeError("импульс удара не сохранился")
        if self.v2 - self.v1 != self.e * self.u:
            raise RuntimeError("коэффициент восстановления не сошёлся")
        self.answer = self.v1 if self.task_type == "first_speed" else self.v2
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Тело массы {self.m1} кг со скоростью {self.u} м/с ударяет покоящееся тело массы "
                 f"{self.m2} кг. Удар центральный, коэффициент восстановления e = {self.e}. "
                 f"Положительное направление — начальная скорость первого тела. "
                 f"Найдите скорость {'первого' if self.task_type == 'first_speed' else 'второго'} "
                 f"тела после удара, в м/с.") if ru else
                (f"A body of mass {self.m1} kg at {self.u} m/s hits a body of mass {self.m2} kg at rest. "
                 f"The collision is head-on with coefficient of restitution e = {self.e}. "
                 f"The positive direction is the first body's initial velocity. "
                 f"Find the speed of the "
                 f"{'first' if self.task_type == 'first_speed' else 'second'} body after impact, in m/s."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"v1 = (m1 - e*m2) / (m1 + m2) * u = {self.v1}, "
                 f"v2 = m1*(1 + e) / (m1 + m2) * u = {self.v2}.") if ru else
                (f"v1 = (m1 - e*m2) / (m1 + m2) * u = {self.v1}, "
                 f"v2 = m1*(1 + e) / (m1 + m2) * u = {self.v2}."))
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
