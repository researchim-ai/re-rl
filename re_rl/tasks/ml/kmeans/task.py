"""KMeansStepTask — один шаг k-means с двумя центроидами.

Близость — квадрат евклидова расстояния (корень не нужен и не сравнивается).
При равенстве точка достаётся центроиду 1.

Подтипы:
- ``nearest`` — какому центроиду ближе запрос (1 или 2);
- ``count``   — сколько точек выборки попадает в кластер 1;
- ``mean_x``  — новая x-координата центроида 1 (точная дробь).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Point = Tuple[int, int]


def sqdist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def assign_to_first(point: Point, c1: Point, c2: Point) -> bool:
    d1, d2 = sqdist(point, c1), sqdist(point, c2)
    return d1 <= d2


class KMeansStepTask(BaseMathTask):
    TASK_TYPE = "kmeans_step"
    TASK_TYPES = ["nearest", "count", "mean_x"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "span": 4}, 2: {"n": 4, "span": 4}, 3: {"n": 5, "span": 5},
        4: {"n": 6, "span": 5}, 5: {"n": 6, "span": 6}, 6: {"n": 8, "span": 6},
        7: {"n": 8, "span": 7}, 8: {"n": 10, "span": 7}, 9: {"n": 10, "span": 8},
        10: {"n": 12, "span": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.span = int(p["span"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        for _ in range(40):
            self.c1 = (random.randint(-self.span, self.span), random.randint(-self.span, self.span))
            self.c2 = (random.randint(-self.span, self.span), random.randint(-self.span, self.span))
            if self.c1 == self.c2:
                self.c2 = (self.c1[0] + 1, self.c1[1])
            self.points = [(random.randint(-self.span, self.span), random.randint(-self.span, self.span))
                           for _ in range(self.n)]
            self.query = (random.randint(-self.span, self.span), random.randint(-self.span, self.span))
            self.in_first = [assign_to_first(p, self.c1, self.c2) for p in self.points]
            if any(self.in_first):
                break
        if not any(self.in_first):
            self.points[0] = self.c1
            self.in_first[0] = True
        self.count = sum(self.in_first)
        sx = sum(p[0] for p, flag in zip(self.points, self.in_first) if flag)
        self.mean_x = Fraction(sx, self.count)
        self.nearest = 1 if assign_to_first(self.query, self.c1, self.c2) else 2

    def _pts(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self.points)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        centers = ((texts.t('s1', language, c1=self.c1, c2=self.c2)))
        if self.task_type == "nearest":
            ask = ((texts.t('s2', language, query=self.query)))
        elif self.task_type == "count":
            ask = ((texts.t('s4', language, v0=self._pts())))
        else:
            ask = ((texts.t('s5', language, v0=self._pts())))
        return f"{rule} {centers} {ask}"

    def solve(self):
        from re_rl.tasks.ml.detailed_solvers import solve_detailed
        solve_detailed(self)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "mean_x":
            return verify_fraction(prediction, self.mean_x)
        truth = self.nearest if self.task_type == "nearest" else self.count
        return U.verify_int(prediction, int(truth))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
