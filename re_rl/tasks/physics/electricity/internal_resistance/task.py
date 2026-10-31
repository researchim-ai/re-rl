"""InternalResistanceTask — ЭДС и внутреннее сопротивление источника.

Два режима: V = E - I*r. Числа подобраны так, что E и r — целые, а напряжение положительно.

Подтипы: ``resistance`` и ``emf``.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
            raise RuntimeError(texts.t('s5', language))
        self.answer = self.r if self.task_type == "resistance" else self.emf
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = ((texts.t('s0', language, i1=self.i1, v1=self.v1, i2=self.i2, v2=self.v2)))
        law = ((texts.t('s1', language)))
        if self.task_type == "resistance":
            ask = ((texts.t('s3', language)))
        else:
            ask = ((texts.t('s4', language)))
        return f"{data} {law} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = ((texts.t('s2', self.language, v1=self.v1, v2=self.v2, i2=self.i2, i1=self.i1, r=self.r, v1_2=self.v1, i1_2=self.i1, r_2=self.r, emf=self.emf)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
