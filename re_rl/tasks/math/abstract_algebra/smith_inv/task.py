"""SmithInvTask — инвариантные множители прямой суммы циклических групп.

Новый циклический порядок вплетается через наибольший общий делитель и наименьшее общее кратное.
Число слагаемых растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from sympy.matrices.normalforms import smith_normal_form
import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return abs(left)


def smith_trace(orders: Sequence[int]) -> List[Tuple[int, int, int]]:
    factors: List[int] = []
    trace = []
    for order in orders:
        if order < 1:
            raise RuntimeError("factor mismatch")
        acc = order
        updated = []
        for item in factors:
            gap = _gcd(item, acc)
            updated.append(gap)
            acc = (item // gap) * acc
        updated.append(acc)
        factors = updated
        for index in range(len(factors) - 1):
            if factors[index + 1] % factors[index] != 0:
                raise RuntimeError("factor mismatch")
        count = sum(1 for item in factors if item > 1)
        trace.append((factors[0], factors[-1], count))
    product = 1
    for order in orders:
        product *= order
    got = 1
    for item in factors:
        got *= item
    if got != product:
        raise RuntimeError("factor mismatch")
    form = smith_normal_form(sp.diag(*[int(order) for order in orders]))
    diagonal = [int(form[index, index]) for index in range(form.rows)]
    if diagonal != factors:
        raise RuntimeError("factor mismatch")
    return trace


class SmithInvTask(BaseMathTask):
    TASK_TYPE = "smith_inv"
    TASK_TYPES = ["count", "last"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.orders = [random.randint(1, 18) for _ in range(self.n)]
        self.trace = smith_trace(self.orders)
        self.count = self.trace[-1][2]
        self.last = self.trace[-1][1]
        self.answer = self.count if self.task_type == "count" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(order) for order in self.orders)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, first=first, last=last, count=count)
            for index, (first, last, count) in enumerate(self.trace, 1)
        ]
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
