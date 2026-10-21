"""InductorEnergyTask — энергия катушки в выбранных единицах.

U = L * I^2 / 2. Ток в обратной задаче — положительный корень, и он целый.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def inductor_energy(inductance: int, current: int) -> Fraction:
    return Fraction(inductance * current * current, 2)


class InductorEnergyTask(BaseMathTask):
    TASK_TYPE = "inductor_energy"
    TASK_TYPES = ["energy", "inductance", "current"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 4}, 2: {"m": 5}, 3: {"m": 6}, 4: {"m": 6}, 5: {"m": 8},
        6: {"m": 8}, 7: {"m": 10}, 8: {"m": 12}, 9: {"m": 14}, 10: {"m": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.inductance = random.randint(1, limit)
        self.current = random.randint(1, limit)
        self.energy = inductor_energy(self.inductance, self.current)
        self.answer = {
            "energy": self.energy,
            "inductance": Fraction(self.inductance),
            "current": Fraction(self.current),
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        energy = fmt_fraction(self.energy)
        if self.task_type == "energy":
            ask = ((texts.t('s1', language, inductance=self.inductance, current=self.current)))
        elif self.task_type == "inductance":
            ask = ((texts.t('s2', language, energy=energy, current=self.current)))
        else:
            ask = ((texts.t('s3', language, energy=energy, inductance=self.inductance)))
        return f"{law} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((f"U = {self.inductance} * {self.current}^2 / 2 = {fmt_fraction(self.energy)}."))
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
