"""PolicyExpectationTask — оценка политики как среднее Q по π.

π задаётся целыми весами: вероятность действия = вес / сумма весов.
V = sum π(a) Q(a). Преимущество действия = Q(a) - V.
Обе величины — точные дроби.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def policy_value(weights: List[int], q_values: List[int]) -> Fraction:
    total = sum(weights)
    acc = Fraction(0)
    for weight, q_value in zip(weights, q_values):
        acc += Fraction(weight, total) * q_value
    return acc


class PolicyExpectationTask(BaseMathTask):
    TASK_TYPE = "policy_expectation"
    TASK_TYPES = ["value", "advantage"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 5}, 2: {"n": 2, "mag": 6}, 3: {"n": 3, "mag": 6},
        4: {"n": 3, "mag": 8}, 5: {"n": 3, "mag": 8}, 6: {"n": 4, "mag": 10},
        7: {"n": 4, "mag": 10}, 8: {"n": 4, "mag": 12}, 9: {"n": 5, "mag": 12},
        10: {"n": 5, "mag": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.weights = [random.randint(1, self.mag) for _ in range(self.n)]
        self.q_values = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.value = policy_value(self.weights, self.q_values)
        self.action = random.randrange(self.n)
        self.advantage = self.q_values[self.action] - self.value
        self.answer = self.value if self.task_type == "value" else self.advantage
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rows(self) -> str:
        return ", ".join(
            texts.t('s4', self.language, v0=i + 1, w=w, q=q) for i, (w, q) in enumerate(zip(self.weights, self.q_values))
        )

    def _rows_en(self) -> str:
        return ", ".join(
            f"{i + 1}: weight {w}, Q {q}" for i, (w, q) in enumerate(zip(self.weights, self.q_values))
        )

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        data = ({"ru": (self._rows()), "en": (self._rows_en())}.get(language, (self._rows_en())))
        if self.task_type == "value":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language, v0=self.action + 1)))
        return f"{rule} {data}. {ask}"

    def solve(self):
        from re_rl.tasks.rl.detailed_solvers import solve_detailed
        solve_detailed(self)

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
