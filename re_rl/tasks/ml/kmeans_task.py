"""KMeansStepTask — один шаг k-means с двумя центроидами.

Близость — квадрат евклидова расстояния (корень не нужен и не сравнивается).
При равенстве точка достаётся центроиду 1.

Подтипы:
- ``nearest`` — какому центроиду ближе запрос (1 или 2);
- ``count``   — сколько точек выборки попадает в кластер 1;
- ``mean_x``  — новая x-координата центроида 1 (точная дробь).
"""

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
        ru = language == "ru"
        rule = (("Два центроида. Точка относится к тому, у кого меньше квадрат расстояния "
                 "(dx^2 + dy^2). При равенстве выбирается центроид 1.") if ru else
                ("Two centroids. A point goes to the centroid with the smaller squared distance "
                 "(dx^2 + dy^2). Ties go to centroid 1."))
        centers = ((f"Центроид 1 = {self.c1}, центроид 2 = {self.c2}.") if ru else
                   (f"Centroid 1 = {self.c1}, centroid 2 = {self.c2}."))
        if self.task_type == "nearest":
            ask = ((f"К какому центроиду ближе точка {self.query}? Ответьте 1 или 2.") if ru else
                   (f"Which centroid is closer to {self.query}? Answer 1 or 2."))
        elif self.task_type == "count":
            ask = ((f"Точки: {self._pts()}. Сколько из них попадёт в кластер 1?") if ru else
                   (f"Points: {self._pts()}. How many are assigned to cluster 1?"))
        else:
            ask = ((f"Точки: {self._pts()}. После назначения найдите новую x-координату центроида 1 "
                    f"(среднее x точек кластера). Ответ — целое или несократимая дробь.") if ru else
                   (f"Points: {self._pts()}. After assignment, find the new x-coordinate of centroid 1 "
                    f"(the mean x of its points). Answer with an integer or a reduced fraction."))
        return f"{rule} {centers} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "nearest":
            d1, d2 = sqdist(self.query, self.c1), sqdist(self.query, self.c2)
            step = ((f"Квадраты расстояний до 1 и 2: {d1} и {d2}.") if ru else
                    (f"Squared distances to 1 and 2: {d1} and {d2}."))
            self.final_answer = str(self.nearest)
        elif self.task_type == "count":
            step = ((f"В кластер 1 попадает {self.count} точек.") if ru else
                    (f"{self.count} points go to cluster 1."))
            self.final_answer = str(self.count)
        else:
            shown = fmt_fraction(self.mean_x)
            step = ((f"Среднее x кластера 1 равно {shown}.") if ru else
                    (f"Mean x of cluster 1 is {shown}."))
            self.final_answer = shown
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

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
