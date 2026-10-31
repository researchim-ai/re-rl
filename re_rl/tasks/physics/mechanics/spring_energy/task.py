"""SpringEnergyTask — энергия пружины k * x^2 / 2.

Ответ — точная дробь. Подтипы: энергия и жёсткость при известных энергии и удлинении.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class SpringEnergyTask(BaseMathTask):
    TASK_TYPE = "spring_energy"
    TASK_TYPES = ["energy", "stiffness"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 6, "x": 4}, 2: {"k": 8, "x": 5}, 3: {"k": 8, "x": 6},
        4: {"k": 10, "x": 6}, 5: {"k": 12, "x": 6}, 6: {"k": 12, "x": 8},
        7: {"k": 15, "x": 8}, 8: {"k": 16, "x": 8}, 9: {"k": 20, "x": 9},
        10: {"k": 24, "x": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.k = random.randint(1, int(p["k"]))
        self.x = random.randint(1, int(p["x"]))
        self.energy = Fraction(self.k * self.x * self.x, 2)
        self.answer = self.energy if self.task_type == "energy" else Fraction(self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "energy":
            ask = ((texts.t('s1', language, k=self.k, x=self.x)))
        else:
            ask = ((texts.t('s2', language, v0=fmt_fraction(self.energy), x=self.x)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((f"E = {self.k} * {self.x}^2 / 2 = {fmt_fraction(self.energy)}."))
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
