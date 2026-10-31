"""CyclotronTask — циклотронная частота в выбранных единицах.

ω = q * B / m. Постоянная перед формулой равна 1, ответ — точная дробь.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def cyclotron_omega(charge: int, field: int, mass: int) -> Fraction:
    return Fraction(charge * field, mass)


class CyclotronTask(BaseMathTask):
    TASK_TYPE = "cyclotron"
    TASK_TYPES = ["frequency", "charge", "mass"]

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
        self.charge = random.randint(1, limit)
        self.field = random.randint(1, limit)
        self.mass = random.randint(1, limit)
        self.omega = cyclotron_omega(self.charge, self.field, self.mass)
        self.answer = {
            "frequency": self.omega,
            "charge": Fraction(self.charge),
            "mass": Fraction(self.mass),
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        omega = fmt_fraction(self.omega)
        if self.task_type == "frequency":
            ask = ((texts.t('s2', language, charge=self.charge, field=self.field, mass=self.mass)))
        elif self.task_type == "charge":
            ask = ((texts.t('s3', language, omega=omega, field=self.field, mass=self.mass)))
        else:
            ask = ((texts.t('s4', language, omega=omega, charge=self.charge, field=self.field)))
        return f"{law} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, charge=self.charge, field=self.field, mass=self.mass, v3=fmt_fraction(self.omega))))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
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
