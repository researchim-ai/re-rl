"""PolicyExpectationTask — оценка политики как среднее Q по π.

π задаётся целыми весами: вероятность действия = вес / сумма весов.
V = sum π(a) Q(a). Преимущество действия = Q(a) - V.
Обе величины — точные дроби.
"""

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
            f"{i + 1}: вес {w}, Q {q}" for i, (w, q) in enumerate(zip(self.weights, self.q_values))
        )

    def _rows_en(self) -> str:
        return ", ".join(
            f"{i + 1}: weight {w}, Q {q}" for i, (w, q) in enumerate(zip(self.weights, self.q_values))
        )

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Вероятность действия = его вес / сумма весов. "
                 "Оценка политики V = сумма π(a) * Q(a). "
                 "Преимущество действия = Q(a) - V. Ответ — целое или несократимая дробь.")
                if ru else
                ("An action's probability is its weight over the total weight. "
                 "The policy value V is the sum of π(a) * Q(a). "
                 "An action's advantage is Q(a) - V. Answer with an integer or a reduced fraction."))
        data = self._rows() if ru else self._rows_en()
        if self.task_type == "value":
            ask = ("Найдите V." if ru else "Find V.")
        else:
            ask = ((f"Найдите преимущество действия {self.action + 1}.") if ru else
                   (f"Find the advantage of action {self.action + 1}."))
        return f"{rule} {data}. {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"V = {fmt_fraction(self.value)}, преимущество выбранного действия = {fmt_fraction(self.advantage)}.")
                if ru else
                (f"V = {fmt_fraction(self.value)}, advantage of the chosen action = {fmt_fraction(self.advantage)}."))
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
