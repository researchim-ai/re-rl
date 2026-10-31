"""ResistorPairTask — два резистора последовательно и параллельно.

Последовательное сопротивление — сумма. Параллельное — r1*r2/(r1+r2), точная дробь.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def pair_resistance(r1: int, r2: int):
    return r1 + r2, Fraction(r1 * r2, r1 + r2)


class ResistorPairTask(BaseMathTask):
    TASK_TYPE = "resistor_pair"
    TASK_TYPES = ["series", "parallel"]

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
        self.r1 = random.randint(1, limit)
        self.r2 = random.randint(1, limit)
        self.series, self.parallel = pair_resistance(self.r1, self.r2)
        self.answer = Fraction(self.series) if self.task_type == "series" else self.parallel
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = ((texts.t('s0', language, r1=self.r1, r2=self.r2)))
        if self.task_type == "series":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{data} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = ((texts.t('s1', self.language, series=self.series, v1=fmt_fraction(self.parallel))))
        shown = fmt_fraction(self.answer)
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
