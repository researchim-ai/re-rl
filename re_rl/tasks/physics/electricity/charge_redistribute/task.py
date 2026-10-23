"""ChargeRedistributeTask — последовательное выравнивание зарядов.

Ёмкости равны, поэтому при соединении пары оба заряда становятся половиной суммы.
Порядок соединений задан, итог на выбранном конденсаторе — сокращённая дробь.
Число соединений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def show_fraction(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def share_sequence(charges: Sequence[int], links: Sequence[int]) -> List[Fraction]:
    state = [Fraction(charge) for charge in charges]
    for link in links:
        average = (state[link] + state[link + 1]) / 2
        state[link] = average
        state[link + 1] = average
    return state


class ChargeRedistributeTask(BaseMathTask):
    TASK_TYPE = "charge_redistribute"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 5}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 6}, 8: {"n": 7, "m": 6}, 9: {"n": 8, "m": 6},
        10: {"n": 10, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.charges = [random.randint(1, limit) for _ in range(self.n)]
        self.links = [random.randint(0, self.n - 2) for _ in range(self.n)]
        self.k = random.randint(1, self.n)
        self.final_charges = share_sequence(self.charges, self.links)
        self.chosen = self.final_charges[self.k - 1]
        self.numer = self.chosen.numerator
        self.denom = self.chosen.denominator
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        charges = ", ".join(str(charge) for charge in self.charges)
        links = ", ".join(f"{link + 1}-{link + 2}" for link in self.links)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, charges=charges, links=links, k=self.k)

    def solve(self):
        state = [Fraction(charge) for charge in self.charges]
        steps = []
        for index, link in enumerate(self.links, 1):
            average = (state[link] + state[link + 1]) / 2
            state[link] = average
            state[link + 1] = average
            steps.append(texts.t(
                "s2", self.language, i=index, left=link + 1, right=link + 2,
                value=show_fraction(average),
            ))
        steps.append(texts.t(
            "s3", self.language, k=self.k, numer=self.numer, denom=self.denom,
        ))
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
