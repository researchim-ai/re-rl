"""LagrangeInterpolationTask — значение интерполяционного многочлена Лагранжа.

Узлы строятся по многочлену с целыми коэффициентами, поэтому значение в целой
точке — целое. Независимая проверка подставляет те же узлы в формулу Лагранжа
на ``fractions.Fraction`` и требует точного совпадения.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lagrange_at(xs: Sequence[int], ys: Sequence[int], xq: int) -> Fraction:
    """Точное значение интерполяционного многочлена в точке ``xq``."""
    total = Fraction(0)
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = Fraction(yi)
        for j, xj in enumerate(xs):
            if i != j:
                term *= Fraction(xq - xj, xi - xj)
        total += term
    return total


def _eval_poly(coeffs: Sequence[int], x: int) -> int:
    """coeffs[k] — коэффициент при x^k."""
    acc = 0
    pow_x = 1
    for c in coeffs:
        acc += c * pow_x
        pow_x *= x
    return acc


class LagrangeInterpolationTask(BaseMathTask):
    TASK_TYPE = "lagrange_interpolation"
    TASK_TYPES = ["value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 1, "coef": 2}, 2: {"degree": 1, "coef": 3},
        3: {"degree": 2, "coef": 2}, 4: {"degree": 2, "coef": 3},
        5: {"degree": 2, "coef": 4}, 6: {"degree": 3, "coef": 3},
        7: {"degree": 3, "coef": 3}, 8: {"degree": 3, "coef": 4},
        9: {"degree": 4, "coef": 3}, 10: {"degree": 4, "coef": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.degree = int(p["degree"])
        self.coef = int(p["coef"])
        self.task_type = "value"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        n = self.degree + 1  # число узлов
        self.coeffs = [random.randint(-self.coef, self.coef) for _ in range(n)]
        if all(c == 0 for c in self.coeffs[1:]):
            self.coeffs[1] = random.choice([-1, 1])
        pool = list(range(-self.degree - 1, self.degree + 4))
        self.xs = sorted(random.sample(pool, n))
        self.ys = [_eval_poly(self.coeffs, x) for x in self.xs]
        outside = [x for x in range(min(self.xs) - 2, max(self.xs) + 3) if x not in self.xs]
        self.xq = random.choice(outside)
        exact = lagrange_at(self.xs, self.ys, self.xq)
        direct = _eval_poly(self.coeffs, self.xq)
        if exact != direct or exact.denominator != 1:
            raise RuntimeError(texts.t('s3', self.language))
        self.answer = int(exact)
        self.terms = self._terms()

    def _terms(self) -> List[Fraction]:
        terms = []
        for i, (xi, yi) in enumerate(zip(self.xs, self.ys)):
            term = Fraction(yi)
            for j, xj in enumerate(self.xs):
                if i != j:
                    term *= Fraction(self.xq - xj, xi - xj)
            terms.append(term)
        return terms

    def _points(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in zip(self.xs, self.ys))

    def _descr(self, language):
        pts = self._points()
        return ((texts.t('s0', language, pts=pts, degree=self.degree, xq=self.xq)))

    def solve(self):
        shown = ", ".join(f"{t.numerator}/{t.denominator}" if t.denominator != 1 else str(t.numerator)
                          for t in self.terms)
        self.solution_steps = [
            ((texts.t('s1', self.language, xq=self.xq, shown=shown))),
            ((texts.t('s2', self.language, answer=self.answer))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
