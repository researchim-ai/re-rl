"""KalmanTask — несколько одномерных обновлений Калмана для постоянной величины.

Между измерениями дисперсия не растёт. 
K = p / (p + r), m = m + K * (z - m), p = p * r / (p + r).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Observation = Tuple[int, int]


def kalman_filter(mean: int, variance: int, observations: Sequence[Observation]) -> Tuple[Fraction, Fraction]:
    posterior = Fraction(mean)
    spread = Fraction(variance)
    for measurement, noise in observations:
        gain = spread / (spread + noise)
        posterior = posterior + gain * (measurement - posterior)
        spread = spread * noise / (spread + noise)
    return posterior, spread


class KalmanUpdateTask(BaseMathTask):
    TASK_TYPE = "kalman_update"
    TASK_TYPES = ["mean", "variance"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 1, "mag": 4}, 2: {"k": 2, "mag": 4}, 3: {"k": 2, "mag": 5},
        4: {"k": 3, "mag": 5}, 5: {"k": 3, "mag": 6}, 6: {"k": 4, "mag": 6},
        7: {"k": 4, "mag": 8}, 8: {"k": 5, "mag": 8}, 9: {"k": 5, "mag": 10},
        10: {"k": 6, "mag": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.k = int(p["k"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.prior_mean = random.randint(-self.mag, self.mag)
        self.prior_var = random.randint(1, self.mag)
        self.observations = [
            (random.randint(-self.mag, self.mag), random.randint(1, self.mag))
            for _ in range(self.k)
        ]
        self.mean, self.variance = kalman_filter(self.prior_mean, self.prior_var, self.observations)
        self.answer = self.mean if self.task_type == "mean" else self.variance
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return "; ".join(f"z={z}, r={noise}" for z, noise in self.observations)

    def _descr(self, language):
        rule = ((texts.t('s0', language, prior_mean=self.prior_mean, prior_var=self.prior_var, v2=self._shown())))
        ask = (((texts.t('s2', language)))
               if self.task_type == "mean" else
               ((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, v0=fmt_fraction(self.mean), v1=fmt_fraction(self.variance))))
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
