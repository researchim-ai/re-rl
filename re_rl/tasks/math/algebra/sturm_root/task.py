"""SturmRootTask — число различных вещественных корней по цепочке Штурма.

Остаток меняет знак и делится на положительный общий делитель. Перемены знака на концах вычитаются.
Степень многочлена растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _trim(poly: Sequence[Fraction]) -> List[Fraction]:
    index = 0
    values = [Fraction(coeff) for coeff in poly]
    while index < len(values) - 1 and values[index] == 0:
        index += 1
    return values[index:]


def _degree(poly: Sequence[Fraction]) -> int:
    return len(_trim(poly)) - 1


def _primitive(poly: Sequence[Fraction]) -> List[int]:
    values = _trim(poly)
    if not any(values):
        return [0]
    common_den = 1
    for coeff in values:
        common_den = math.lcm(common_den, coeff.denominator)
    numbers = [int(coeff * common_den) for coeff in values]
    gap = 0
    for number in numbers:
        gap = math.gcd(gap, abs(number))
    gap = max(gap, 1)
    return [number // gap for number in numbers]


def _remainder(first: Sequence[int], second: Sequence[int]) -> List[Fraction]:
    divisor = _trim(second)
    rest = [Fraction(coeff) for coeff in first]
    while _trim(rest) != [0] and _degree(_trim(rest)) >= _degree(divisor):
        rest = _trim(rest)
        factor = rest[0] / divisor[0]
        for index, coeff in enumerate(divisor):
            rest[index] -= factor * coeff
    return _trim(rest)


def _derivative(poly: Sequence[int]) -> List[int]:
    degree = len(poly) - 1
    if degree <= 0:
        return [0]
    raw = [poly[index] * (degree - index) for index in range(degree)]
    return _primitive(raw)


def _sequence(coeffs: Sequence[int]) -> List[List[int]]:
    first = _primitive(coeffs)
    second = _derivative(first)
    seq = [first]
    if any(second):
        seq.append(second)
    while _degree(seq[-1]) > 0:
        nxt = _primitive([-coeff for coeff in _remainder(seq[-2], seq[-1])])
        if not any(nxt):
            break
        seq.append(nxt)
    return seq


def _eval(poly: Sequence[int], point: int) -> int:
    acc = 0
    for coeff in poly:
        acc = acc * point + coeff
    return acc


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)


def sturm_trace(coeffs: Sequence[int], left: int, right: int) -> List[Tuple[int, int]]:
    seq = _sequence(coeffs)
    if _eval(seq[0], left) == 0 or _eval(seq[0], right) == 0:
        raise RuntimeError("root mismatch")
    left_changes = right_changes = 0
    left_sign = right_sign = 0
    trace = []
    for poly in seq:
        sign_left = _sign(_eval(poly, left))
        sign_right = _sign(_eval(poly, right))
        if sign_left and left_sign and sign_left != left_sign:
            left_changes += 1
        if sign_right and right_sign and sign_right != right_sign:
            right_changes += 1
        if sign_left:
            left_sign = sign_left
        if sign_right:
            right_sign = sign_right
        trace.append((left_changes, right_changes))
    if left_changes < right_changes:
        raise RuntimeError("root mismatch")
    symbol = sp.symbols("x")
    roots = []
    for root in sp.real_roots(sp.Poly(list(coeffs), symbol)):
        if all(root != old for old in roots):
            roots.append(root)
    expect = sum(1 for root in roots if root > left and root <= right)
    if left_changes - right_changes != expect:
        raise RuntimeError("root mismatch")
    return trace


class SturmRootTask(BaseMathTask):
    TASK_TYPE = "sturm_root"
    TASK_TYPES = ["roots", "lefts"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.left = -2
        self.right = 3
        self.coeffs: List[int] = []
        self.trace: List[Tuple[int, int]] = []
        for _ in range(2000):
            coeffs = [random.randint(-2, 2) for _ in range(self.n + 1)]
            coeffs[0] = random.choice([-2, -1, 1, 2])
            seq = _sequence(coeffs)
            if len(seq) != self.n + 1:
                continue
            if any(abs(coeff) > 10 ** 6 for poly in seq for coeff in poly):
                continue
            if _eval(seq[0], self.left) == 0 or _eval(seq[0], self.right) == 0:
                continue
            self.coeffs = coeffs
            self.trace = sturm_trace(coeffs, self.left, self.right)
            break
        if len(self.trace) != self.n + 1:
            raise RuntimeError("root mismatch")
        self.lefts = self.trace[-1][0]
        self.roots = self.lefts - self.trace[-1][1]
        self.answer = self.roots if self.task_type == "roots" else self.lefts
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(coeff) for coeff in self.coeffs)

    def _descr(self, language):
        key = "s0" if self.task_type == "roots" else "s1"
        return texts.t(
            key, language, n=self.n, listing=self._listing(), left=self.left, right=self.right,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, lefts=lefts, rights=rights)
            for index, (lefts, rights) in enumerate(self.trace, 1)
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
