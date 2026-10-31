"""PendulumRatioTask — математический маятник без корня и без π в ответе.

Из T = 2π * sqrt(L/g) следует (T / 2π)^2 = L/g.
Спрашивается эта дробь либо длина при известном g.

Подтипы: ``ratio`` и ``length``.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class PendulumRatioTask(BaseMathTask):
    TASK_TYPE = "pendulum_ratio"
    TASK_TYPES = ["ratio", "length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 6}, 2: {"m": 8}, 3: {"m": 8}, 4: {"m": 10}, 5: {"m": 12},
        6: {"m": 12}, 7: {"m": 15}, 8: {"m": 16}, 9: {"m": 20}, 10: {"m": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.length = random.randint(1, limit)
        self.gravity = random.randint(1, limit)
        self.ratio = Fraction(self.length, self.gravity)
        self.answer = self.ratio if self.task_type == "ratio" else Fraction(self.length)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "ratio":
            ask = ((texts.t('s1', language, length=self.length, gravity=self.gravity)))
        else:
            ask = ((texts.t('s2', language, gravity=self.gravity, v1=fmt_fraction(self.ratio))))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((f"L/g = {self.length}/{self.gravity} = {fmt_fraction(self.ratio)}."))
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
