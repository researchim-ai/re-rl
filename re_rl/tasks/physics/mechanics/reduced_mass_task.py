"""ReducedMassTask — приведённая масса двух тел.

μ = m1 * m2 / (m1 + m2). Обратная величина равна 1/m1 + 1/m2.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def reduced_pair(m1: int, m2: int) -> Tuple[Fraction, Fraction]:
    reduced = Fraction(m1 * m2, m1 + m2)
    reciprocal = Fraction(m1 + m2, m1 * m2)
    return reduced, reciprocal


class ReducedMassTask(BaseMathTask):
    TASK_TYPE = "reduced_mass"
    TASK_TYPES = ["reduced", "reciprocal"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 6}, 2: {"m": 8}, 3: {"m": 8}, 4: {"m": 10}, 5: {"m": 12},
        6: {"m": 14}, 7: {"m": 16}, 8: {"m": 18}, 9: {"m": 20}, 10: {"m": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.m1 = random.randint(1, limit)
        self.m2 = random.randint(1, limit)
        self.reduced, self.reciprocal = reduced_pair(self.m1, self.m2)
        self.answer = self.reduced if self.task_type == "reduced" else self.reciprocal
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = ((f"Две массы: m1 = {self.m1}, m2 = {self.m2}.") if ru else
                (f"Two masses: m1 = {self.m1}, m2 = {self.m2}."))
        if self.task_type == "reduced":
            ask = (("Приведённая масса μ = m1 * m2 / (m1 + m2). Найдите μ. "
                    "Ответ — целое или несократимая дробь.") if ru else
                   ("The reduced mass is μ = m1 * m2 / (m1 + m2). Find μ. "
                    "Answer with an integer or a reduced fraction."))
        else:
            ask = (("Найдите 1/μ. Это сумма 1/m1 + 1/m2. "
                    "Ответ — целое или несократимая дробь.") if ru else
                   ("Find 1/μ. It equals 1/m1 + 1/m2. "
                    "Answer with an integer or a reduced fraction."))
        return f"{data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"μ = {fmt_fraction(self.reduced)}, 1/μ = {fmt_fraction(self.reciprocal)}.") if ru else
                (f"μ = {fmt_fraction(self.reduced)}, 1/μ = {fmt_fraction(self.reciprocal)}."))
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
