"""CycloEvalTask — значение кругового многочлена в целой точке.

Коэффициенты берёт точная библиотека, значение считается схемой Горнера.
Номер многочлена растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ORDERS = {
    1: 5, 2: 5, 3: 7, 4: 11, 5: 13,
    6: 17, 7: 19, 8: 23, 9: 29, 10: 31,
}


def cyclo_coeffs(order: int) -> List[int]:
    symbol = sp.symbols("x")
    poly = sp.Poly(sp.cyclotomic_poly(order, symbol), symbol)
    return [int(coeff) for coeff in poly.all_coeffs()]


def cyclo_trace(coeffs: List[int], point: int) -> List[int]:
    acc = 0
    trace = []
    for coeff in coeffs:
        acc = acc * point + coeff
        trace.append(acc)
    return trace


class CycloEvalTask(BaseMathTask):
    TASK_TYPE = "cyclo_eval"
    TASK_TYPES = ["value", "degree"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        level: {"n": order} for level, order in _ORDERS.items()
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.order = max(2, int(p["n"]))
        self.n = self.order
        self.point = 2
        self.coeffs = cyclo_coeffs(self.order)
        self.trace = cyclo_trace(self.coeffs, self.point)
        self.value = self.trace[-1]
        self.degree = len(self.coeffs) - 1
        symbol = sp.symbols("x")
        assert self.value == int(sp.cyclotomic_poly(self.order, symbol).subs(symbol, self.point))
        self.answer = self.value if self.task_type == "value" else self.degree
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(coeff) for coeff in self.coeffs)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, order=self.order, point=self.point, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, acc=acc)
            for index, acc in enumerate(self.trace, 1)
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
