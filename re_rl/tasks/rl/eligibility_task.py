"""EligibilityTraceTask — накапливающийся след затухания.

Сначала каждая координата умножается на γλ, затем к посещённой прибавляется 1.
Номера координат с 1.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_FACTORS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


def accumulating_trace(trace: List[int], gamma: Fraction, lam: Fraction, visited: int) -> List[Fraction]:
    factor = gamma * lam
    updated = [factor * value for value in trace]
    updated[visited] += 1
    return updated


class EligibilityTraceTask(BaseMathTask):
    TASK_TYPE = "eligibility_trace"
    TASK_TYPES = ["visited", "other"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 2, "mag": 2}, 2: {"d": 2, "mag": 3}, 3: {"d": 3, "mag": 3},
        4: {"d": 3, "mag": 4}, 5: {"d": 3, "mag": 5}, 6: {"d": 4, "mag": 5},
        7: {"d": 4, "mag": 6}, 8: {"d": 4, "mag": 7}, 9: {"d": 5, "mag": 8},
        10: {"d": 5, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.dim = int(p["d"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.trace = [random.randint(0, self.mag) for _ in range(self.dim)]
        span = _FACTORS[:1 + min(3, difficulty // 3)]
        self.gamma = random.choice(span)
        self.lam = random.choice(span)
        self.visited = random.randrange(self.dim)
        self.updated = accumulating_trace(self.trace, self.gamma, self.lam, self.visited)
        if self.task_type == "visited":
            self.index = self.visited
        else:
            choices = [i for i in range(self.dim) if i != self.visited]
            self.index = random.choice(choices)
        self.answer = self.updated[self.index]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(map(str, self.trace))
        rule = ((f"Накапливающийся след: каждая координата умножается на γλ, "
                 f"затем к посещённой прибавляется 1. "
                 f"γ = {fmt_fraction(self.gamma)}, λ = {fmt_fraction(self.lam)}. "
                 f"Координаты нумеруются с 1. Ответ — целое или несократимая дробь.") if ru else
                (f"Accumulating trace: every coordinate is multiplied by γλ, "
                 f"then 1 is added to the visited one. "
                 f"γ = {fmt_fraction(self.gamma)}, λ = {fmt_fraction(self.lam)}. "
                 f"Coordinates start at 1. Answer with an integer or a reduced fraction."))
        data = ((f"След: {shown}. Посещена координата {self.visited + 1}.") if ru else
                (f"Trace: {shown}. Visited coordinate: {self.visited + 1}."))
        ask = ((f"Найдите новую координату {self.index + 1}.") if ru else
               (f"Find the new coordinate {self.index + 1}."))
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Новая координата {self.index + 1} равна {shown}.") if ru else
                (f"New coordinate {self.index + 1} is {shown}."))
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
