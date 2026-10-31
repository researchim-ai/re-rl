"""RedshiftTask — красное смещение по двум длинам волны.

z = (λ_obs - λ_rest) / λ_rest. Длины волн целые, z — точная дробь.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def redshift_parts(rest: int, shift: int) -> Tuple[Fraction, int]:
    return Fraction(shift, rest), rest + shift


class RedshiftTask(BaseMathTask):
    TASK_TYPE = "spectral_redshift"
    TASK_TYPES = ["redshift", "observed", "rest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 8}, 2: {"m": 10}, 3: {"m": 12}, 4: {"m": 16}, 5: {"m": 20},
        6: {"m": 24}, 7: {"m": 30}, 8: {"m": 36}, 9: {"m": 40}, 10: {"m": 50},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.rest = random.randint(1, limit)
        self.shift = random.randint(1, limit)
        self.z, self.observed = redshift_parts(self.rest, self.shift)
        self.answer = {
            "redshift": self.z,
            "observed": Fraction(self.observed),
            "rest": Fraction(self.rest),
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        z = fmt_fraction(self.z)
        if self.task_type == "redshift":
            ask = ((texts.t('s2', language, rest=self.rest, observed=self.observed)))
        elif self.task_type == "observed":
            ask = ((texts.t('s3', language, rest=self.rest, z=z)))
        else:
            ask = ((texts.t('s4', language, observed=self.observed, z=z)))
        return f"{law} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, shift=self.shift, rest=self.rest, v2=fmt_fraction(self.z), observed=self.observed)))
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
