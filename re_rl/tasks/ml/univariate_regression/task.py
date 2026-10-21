"""UnivariateRegressionTask — МНК для прямой y = a + b x.

Наклон и свободный член — точные дроби по нормальным уравнениям.
Все x не совпадают, знаменатель наклона не нулевой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Pair = Tuple[int, int]


def fit(points: List[Pair]) -> Tuple[Fraction, Fraction]:
    n = len(points)
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    den = n * sxx - sx * sx
    if den == 0:
        raise ZeroDivisionError(texts.literal('literals.s3'))
    slope = Fraction(n * sxy - sx * sy, den)
    intercept = Fraction(sy, n) - slope * Fraction(sx, n)
    return slope, intercept


class UnivariateRegressionTask(BaseMathTask):
    TASK_TYPE = "univariate_regression"
    TASK_TYPES = ["slope", "intercept"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "c": 3}, 2: {"n": 3, "c": 4}, 3: {"n": 4, "c": 4},
        4: {"n": 4, "c": 5}, 5: {"n": 4, "c": 5}, 6: {"n": 5, "c": 5},
        7: {"n": 5, "c": 6}, 8: {"n": 6, "c": 6}, 9: {"n": 6, "c": 7},
        10: {"n": 7, "c": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.c = int(p["c"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        xs = random.sample(range(-self.c, self.c + 1), self.n)
        self.points = [(x, random.randint(-self.c, self.c)) for x in xs]
        self.slope, self.intercept = fit(self.points)
        self.answer = self.slope if self.task_type == "slope" else self.intercept

    def _pts(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self.points)

    def _descr(self, language):
        what = (texts.t('s0', language) if self.task_type == "slope" else texts.t('s1', language))
        return ((texts.t('s2', language, v0=self._pts(), what=what)))

    def solve(self):
        step = ((f"b = {fmt_fraction(self.slope)}, a = {fmt_fraction(self.intercept)}."))
        shown = fmt_fraction(self.answer)
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
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
