"""PickTheoremTask — формула Пика.

Площадь = I + B/2 - 1, где I — внутренние узлы решётки, B — узлы на границе.
Ответ — точная дробь.

Подтипы: площадь и число внутренних узлов.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def pick_area(interior: int, boundary: int) -> Fraction:
    return Fraction(interior) + Fraction(boundary, 2) - 1


class PickTheoremTask(BaseMathTask):
    TASK_TYPE = "pick_theorem"
    TASK_TYPES = ["area", "interior"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"i": 4, "b": 8}, 2: {"i": 6, "b": 10}, 3: {"i": 8, "b": 12},
        4: {"i": 10, "b": 12}, 5: {"i": 12, "b": 16}, 6: {"i": 14, "b": 16},
        7: {"i": 16, "b": 20}, 8: {"i": 20, "b": 24}, 9: {"i": 24, "b": 28},
        10: {"i": 30, "b": 36},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.interior = random.randint(0, int(p["i"]))
        self.boundary = random.randint(3, int(p["b"]))
        self.area = pick_area(self.interior, self.boundary)
        if self.area <= 0:
            self.interior += 1
            self.area = pick_area(self.interior, self.boundary)
        self.answer = self.area if self.task_type == "area" else Fraction(self.interior)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Формула Пика: площадь = I + B/2 - 1. "
                 "Ответ — целое или несократимая дробь.") if ru else
                ("Pick's theorem: area = I + B/2 - 1. "
                 "Answer with an integer or a reduced fraction."))
        if self.task_type == "area":
            ask = ((f"Внутри многоугольника I = {self.interior} узлов решётки, "
                    f"на границе B = {self.boundary}. Найдите площадь.") if ru else
                   (f"The polygon has I = {self.interior} interior lattice points and "
                    f"B = {self.boundary} boundary lattice points. Find the area."))
        else:
            ask = ((f"Площадь = {fmt_fraction(self.area)}, на границе B = {self.boundary} узлов. "
                    f"Найдите I.") if ru else
                   (f"The area is {fmt_fraction(self.area)}, and B = {self.boundary} boundary points. "
                    f"Find I."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Площадь = {self.interior} + {self.boundary}/2 - 1 = {fmt_fraction(self.area)}.") if ru else
                (f"Area = {self.interior} + {self.boundary}/2 - 1 = {fmt_fraction(self.area)}."))
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
