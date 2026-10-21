"""InternalResistanceTask — ЭДС и внутреннее сопротивление источника.

Два режима: V = E - I*r. Числа подобраны так, что E и r — целые, а напряжение положительно.

Подтипы: ``resistance`` и ``emf``.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class InternalResistanceTask(BaseMathTask):
    TASK_TYPE = "internal_resistance"
    TASK_TYPES = ["resistance", "emf"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 3, "i": 3, "extra": 6}, 2: {"r": 4, "i": 4, "extra": 8},
        3: {"r": 4, "i": 5, "extra": 10}, 4: {"r": 5, "i": 5, "extra": 12},
        5: {"r": 6, "i": 6, "extra": 12}, 6: {"r": 6, "i": 7, "extra": 15},
        7: {"r": 8, "i": 8, "extra": 16}, 8: {"r": 8, "i": 9, "extra": 18},
        9: {"r": 10, "i": 10, "extra": 20}, 10: {"r": 12, "i": 12, "extra": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.r = random.randint(1, int(p["r"]))
        self.i1 = random.randint(1, int(p["i"]))
        self.i2 = self.i1 + random.randint(1, int(p["i"]))
        self.emf = self.i2 * self.r + random.randint(1, int(p["extra"]))
        self.v1 = self.emf - self.i1 * self.r
        self.v2 = self.emf - self.i2 * self.r
        if self.v2 <= 0 or (self.v1 - self.v2) != self.r * (self.i2 - self.i1):
            raise RuntimeError("внутреннее сопротивление не сошлось")
        self.answer = self.r if self.task_type == "resistance" else self.emf
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = ((f"При токе {self.i1} А напряжение на клеммах {self.v1} В, "
                 f"при токе {self.i2} А — {self.v2} В.") if ru else
                (f"At current {self.i1} A the terminal voltage is {self.v1} V, "
                 f"at current {self.i2} A it is {self.v2} V."))
        law = (("Источник: V = E - I*r." ) if ru else ("The source obeys V = E - I*r."))
        if self.task_type == "resistance":
            ask = ("Найдите внутреннее сопротивление r в омах." if ru else
                   "Find the internal resistance r in ohms.")
        else:
            ask = ("Найдите ЭДС E в вольтах." if ru else "Find the emf E in volts.")
        return f"{data} {law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"r = ({self.v1} - {self.v2}) / ({self.i2} - {self.i1}) = {self.r} Ом. "
                 f"E = {self.v1} + {self.i1}*{self.r} = {self.emf} В.") if ru else
                (f"r = ({self.v1} - {self.v2}) / ({self.i2} - {self.i1}) = {self.r} ohm. "
                 f"E = {self.v1} + {self.i1}*{self.r} = {self.emf} V."))
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
