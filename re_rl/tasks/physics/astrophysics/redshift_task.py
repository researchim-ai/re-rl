"""RedshiftTask — красное смещение по двум длинам волны.

z = (λ_obs - λ_rest) / λ_rest. Длины волн целые, z — точная дробь.
"""

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
        ru = language == "ru"
        law = (("Красное смещение z = (λ_obs - λ_rest) / λ_rest. "
                "Ответ — целое или несократимая дробь.") if ru else
               ("Redshift z = (λ_obs - λ_rest) / λ_rest. "
                "Answer with an integer or a reduced fraction."))
        z = fmt_fraction(self.z)
        if self.task_type == "redshift":
            ask = ((f"λ_rest = {self.rest}, λ_obs = {self.observed}. Найдите z.") if ru else
                   (f"λ_rest = {self.rest}, λ_obs = {self.observed}. Find z."))
        elif self.task_type == "observed":
            ask = ((f"λ_rest = {self.rest}, z = {z}. Найдите λ_obs.") if ru else
                   (f"λ_rest = {self.rest}, z = {z}. Find λ_obs."))
        else:
            ask = ((f"λ_obs = {self.observed}, z = {z}. Найдите λ_rest.") if ru else
                   (f"λ_obs = {self.observed}, z = {z}. Find λ_rest."))
        return f"{law} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"z = {self.shift}/{self.rest} = {fmt_fraction(self.z)}, λ_obs = {self.observed}.") if ru else
                (f"z = {self.shift}/{self.rest} = {fmt_fraction(self.z)}, λ_obs = {self.observed}."))
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
