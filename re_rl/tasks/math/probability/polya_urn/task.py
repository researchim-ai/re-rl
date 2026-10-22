"""PolyaUrnTask — вероятность конкретной последовательности в урне Полиа.

Вынутый шар возвращают и кладут ещё один того же цвета. Итоговое число красных зависит только от числа красных тиражей, а вероятность последовательности — от порядка.
Число тиражей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def sequence_probability(red: int, blue: int, colors: List[str]) -> Fraction:
    probability = Fraction(1)
    for color in colors:
        total = red + blue
        if color == "R":
            probability *= Fraction(red, total)
            red += 1
        else:
            probability *= Fraction(blue, total)
            blue += 1
    return probability


class PolyaUrnTask(BaseMathTask):
    TASK_TYPE = "polya_urn"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "c": 3}, 2: {"n": 2, "c": 4}, 3: {"n": 3, "c": 4},
        4: {"n": 4, "c": 4}, 5: {"n": 5, "c": 5}, 6: {"n": 6, "c": 5},
        7: {"n": 7, "c": 5}, 8: {"n": 8, "c": 6}, 9: {"n": 9, "c": 6},
        10: {"n": 10, "c": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["c"]))
        self.red = random.randint(1, limit)
        self.blue = random.randint(1, limit)
        self.sequence: List[str] = []
        red, blue = self.red, self.blue
        for _ in range(self.n):
            if random.randrange(red + blue) < red:
                self.sequence.append("R")
                red += 1
            else:
                self.sequence.append("B")
                blue += 1
        self.probability = sequence_probability(self.red, self.blue, self.sequence)
        self.numer = self.probability.numerator
        self.denom = self.probability.denominator
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(self.sequence)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, red=self.red, blue=self.blue, n=self.n, listing=listing)

    def solve(self):
        steps = []
        red, blue = self.red, self.blue
        for index, color in enumerate(self.sequence, 1):
            total = red + blue
            count = red if color == "R" else blue
            steps.append(texts.t(
                "s2", self.language, i=index, color=color, count=count, total=total,
            ))
            if color == "R":
                red += 1
            else:
                blue += 1
        steps.append(texts.t("s3", self.language, numer=self.numer, denom=self.denom))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
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
