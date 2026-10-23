"""BoostChainTask — цепочка коллинеарных релятивистских приращений.

Каждая скорость — малая доля c. Сложение (u+v)/(1+uv) сохраняет рациональность.
Число приращений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

BOOSTS = (
    Fraction(1, 2), Fraction(1, 3), Fraction(1, 4),
    Fraction(2, 5), Fraction(1, 5), Fraction(3, 5),
)


def show_fraction(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def add_boosts(boosts: Sequence[Fraction]) -> List[Fraction]:
    speed = Fraction(0)
    history = []
    for boost in boosts:
        speed = (speed + boost) / (1 + speed * boost)
        history.append(speed)
    return history


class BoostChainTask(BaseMathTask):
    TASK_TYPE = "boost_chain"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.boosts = [random.choice(BOOSTS) for _ in range(self.n)]
        self.history = add_boosts(self.boosts)
        self.final_speed = self.history[-1]
        self.numer = self.final_speed.numerator
        self.denom = self.final_speed.denominator
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(show_fraction(boost) for boost in self.boosts)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        speed = Fraction(0)
        steps = []
        for index, boost in enumerate(self.boosts, 1):
            before = speed
            speed = (speed + boost) / (1 + speed * boost)
            steps.append(texts.t(
                "s2", self.language, i=index,
                before=show_fraction(before), add=show_fraction(boost), value=show_fraction(speed),
            ))
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
