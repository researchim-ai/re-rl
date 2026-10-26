"""ResChainTask — результант пары многочленов через алгоритм Евклида.

Знак и степень старшего коэффициента переносятся на результант остатка.
Число пар растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _trim(poly: Sequence[Fraction]) -> List[Fraction]:
    index = 0
    values = list(poly)
    while index < len(values) - 1 and values[index] == 0:
        index += 1
    return values[index:]


def _degree(poly: Sequence[Fraction]) -> int:
    return len(_trim(poly)) - 1


def _remainder(first: Sequence[int], second: Sequence[int]) -> List[Fraction]:
    divisor = _trim([Fraction(coeff) for coeff in second])
    if not any(divisor):
        raise RuntimeError("result mismatch")
    rest = [Fraction(coeff) for coeff in first]
    while _trim(rest) != [0] and _degree(_trim(rest)) >= _degree(divisor):
        rest = _trim(rest)
        factor = rest[0] / divisor[0]
        for index, coeff in enumerate(divisor):
            rest[index] -= factor * coeff
    return _trim(rest)


def _pair_result(first: Sequence[int], second: Sequence[int]) -> Tuple[Fraction, int]:
    left = _trim([Fraction(coeff) for coeff in first])
    right = _trim([Fraction(coeff) for coeff in second])
    if not any(right):
        return Fraction(0), _degree(left) if any(left) else 0
    if _degree(right) == 0:
        return right[0] ** _degree(left), 0
    rest = _remainder(left, right)
    if not any(rest):
        return Fraction(0), _degree(right)
    value_rest, degree = _pair_result(right, rest)
    deg_left, deg_right, deg_rest = _degree(left), _degree(right), _degree(rest)
    sign = -1 if (deg_left * deg_right + deg_right * deg_rest) % 2 else 1
    value = sign * (right[0] ** (deg_left - deg_rest)) * value_rest
    return value, degree


def res_trace(pairs: Sequence[Tuple[Sequence[int], Sequence[int]]]) -> List[Tuple[int, int, int]]:
    symbol = sp.symbols("x")
    acc = 0
    shared = 0
    trace = []
    for first, second in pairs:
        value, degree = _pair_result(first, second)
        if value.denominator != 1:
            raise RuntimeError("result mismatch")
        number = int(value)
        expect = sp.resultant(sp.Poly(list(first), symbol), sp.Poly(list(second), symbol))
        common = sp.gcd(sp.Poly(list(first), symbol), sp.Poly(list(second), symbol)).degree()
        if number != expect or degree != common:
            raise RuntimeError("result mismatch")
        acc += number
        shared += degree
        trace.append((number, acc, shared))
    return trace


class ResChainTask(BaseMathTask):
    TASK_TYPE = "res_chain"
    TASK_TYPES = ["total", "shared"]

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
        self.pairs = [self._pair() for _ in range(self.n)]
        self.trace = res_trace(self.pairs)
        self.total = self.trace[-1][1]
        self.shared = self.trace[-1][2]
        self.answer = self.total if self.task_type == "total" else self.shared
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _poly(self, degree: int) -> List[int]:
        coeffs = [random.randint(-3, 3) for _ in range(degree + 1)]
        if coeffs[0] == 0:
            coeffs[0] = random.choice([-2, -1, 1, 2])
        return coeffs

    def _mul_linear(self, poly: Sequence[int], root: int) -> List[int]:
        # (x - root) * poly, high degree first
        out = [0] * (len(poly) + 1)
        for index, coeff in enumerate(poly):
            out[index] += coeff
            out[index + 1] -= coeff * root
        return out

    def _pair(self) -> Tuple[List[int], List[int]]:
        if random.randrange(3) == 0:
            root = random.randint(-2, 2)
            return self._mul_linear(self._poly(1), root), self._mul_linear(self._poly(1), root)
        return self._poly(2), self._poly(2)

    def _listing(self) -> str:
        chunks = []
        for first, second in self.pairs:
            left = " ".join(str(coeff) for coeff in first)
            right = " ".join(str(coeff) for coeff in second)
            chunks.append(left + " || " + right)
        return "; ".join(chunks)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, acc=acc, shared=shared)
            for index, (value, acc, shared) in enumerate(self.trace, 1)
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
