"""BrierScoreTask — оценка Брайера для вероятностных прогнозов.

B = (1/n) * sum (p_i - y_i)^2. Вероятности — дроби, ответ точный.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Pair = Tuple[Fraction, int]


def brier_score(pairs: List[Pair]) -> Fraction:
    total = Fraction(0)
    for prob, label in pairs:
        total += (prob - label) ** 2
    return total / len(pairs)


class BrierScoreTask(BaseMathTask):
    TASK_TYPE = "brier_score"
    TASK_TYPES = ["score"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "den": 2}, 2: {"n": 2, "den": 2}, 3: {"n": 3, "den": 2},
        4: {"n": 3, "den": 4}, 5: {"n": 4, "den": 4}, 6: {"n": 4, "den": 4},
        7: {"n": 5, "den": 5}, 8: {"n": 5, "den": 5}, 9: {"n": 6, "den": 5},
        10: {"n": 6, "den": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.den = int(p["den"])
        self.task_type = "score"
        self.augment = augment
        self.pairs = [
            (Fraction(random.randint(0, self.den), self.den), random.randint(0, 1))
            for _ in range(self.n)
        ]
        self.answer = brier_score(self.pairs)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(f"({fmt_fraction(p)}, {y})" for p, y in self.pairs)
        return ((f"Пары (вероятность класса 1, истинная метка): {shown}. "
                 f"Оценка Брайера — среднее квадратов разностей. "
                 f"Найдите её. Ответ — целое или несократимая дробь.") if ru else
                (f"Pairs (probability of class 1, true label): {shown}. "
                 f"The Brier score is the mean of the squared differences. "
                 f"Find it. Answer with an integer or a reduced fraction."))

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        self.solution_steps = [
            ((f"Среднее (p - y)^2 равно {shown}.") if ru else
             (f"The mean of (p - y)^2 is {shown}.")),
            (f"Ответ: {shown}." if ru else f"Answer: {shown}."),
        ]
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
