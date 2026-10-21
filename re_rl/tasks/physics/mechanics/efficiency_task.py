"""EfficiencyTask — КПД как полезная работа, делённая на затраченную.

Подтипы: сама дробь КПД и полезная работа при известных КПД и затратах.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class EfficiencyTask(BaseMathTask):
    TASK_TYPE = "mechanical_efficiency"
    TASK_TYPES = ["efficiency", "useful"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 8}, 2: {"m": 10}, 3: {"m": 12}, 4: {"m": 12}, 5: {"m": 16},
        6: {"m": 18}, 7: {"m": 20}, 8: {"m": 24}, 9: {"m": 30}, 10: {"m": 36},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.total = random.randint(2, limit)
        self.useful = random.randint(1, self.total)
        self.efficiency = Fraction(self.useful, self.total)
        self.answer = self.efficiency if self.task_type == "efficiency" else Fraction(self.useful)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("КПД = полезная работа / затраченная работа. "
                 "Ответ — целое или несократимая дробь.") if ru else
                ("Efficiency = useful work / input work. "
                 "Answer with an integer or a reduced fraction."))
        if self.task_type == "efficiency":
            ask = ((f"Полезная работа {self.useful}, затраченная {self.total}. Найдите КПД.") if ru else
                   (f"Useful work is {self.useful}, input work is {self.total}. Find the efficiency."))
        else:
            ask = ((f"КПД = {fmt_fraction(self.efficiency)}, затраченная работа {self.total}. "
                    f"Найдите полезную работу.") if ru else
                   (f"Efficiency = {fmt_fraction(self.efficiency)}, input work is {self.total}. "
                    f"Find the useful work."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"КПД = {self.useful}/{self.total} = {fmt_fraction(self.efficiency)}.") if ru else
                (f"Efficiency = {self.useful}/{self.total} = {fmt_fraction(self.efficiency)}."))
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
