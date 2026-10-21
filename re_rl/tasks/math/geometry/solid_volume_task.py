"""SolidVolumeTask — объём тела вращения, делённый на π.

Ответ точная дробь: цилиндр r^2*h, конус r^2*h/3, шар 4*r^3/3.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class SolidVolumeTask(BaseMathTask):
    TASK_TYPE = "solid_volume"
    TASK_TYPES = ["cylinder", "cone", "sphere"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 4, "h": 6}, 2: {"r": 5, "h": 8}, 3: {"r": 6, "h": 9},
        4: {"r": 6, "h": 12}, 5: {"r": 8, "h": 12}, 6: {"r": 8, "h": 15},
        7: {"r": 9, "h": 18}, 8: {"r": 10, "h": 20}, 9: {"r": 12, "h": 24},
        10: {"r": 12, "h": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.rmax = int(p["r"])
        self.hmax = int(p["h"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.r = random.randint(1, self.rmax)
        self.h = random.randint(1, self.hmax)
        if self.task_type == "cylinder":
            self.answer = Fraction(self.r * self.r * self.h)
        elif self.task_type == "cone":
            self.answer = Fraction(self.r * self.r * self.h, 3)
        else:
            self.answer = Fraction(4 * self.r ** 3, 3)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        ask = ("Найдите объём, делённый на π. Ответ — целое или несократимая дробь." if ru else
               "Find the volume divided by pi. Answer with an integer or a reduced fraction.")
        if self.task_type == "cylinder":
            body = ((f"Цилиндр с радиусом {self.r} и высотой {self.h}.") if ru else
                    (f"A cylinder of radius {self.r} and height {self.h}."))
        elif self.task_type == "cone":
            body = ((f"Конус с радиусом основания {self.r} и высотой {self.h}.") if ru else
                    (f"A cone of base radius {self.r} and height {self.h}."))
        else:
            body = ((f"Шар радиуса {self.r}.") if ru else (f"A sphere of radius {self.r}."))
        return f"{body} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        if self.task_type == "cylinder":
            step = f"V/π = {self.r}^2 * {self.h} = {shown}."
        elif self.task_type == "cone":
            step = f"V/π = {self.r}^2 * {self.h} / 3 = {shown}."
        else:
            step = f"V/π = 4 * {self.r}^3 / 3 = {shown}."
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
