"""ComputationalGeometryTask — базовая вычислительная геометрия на плоскости.

Подтипы:
- ``convex_hull``          — число вершин выпуклой оболочки набора точек;
- ``segment_intersection``— пересекаются ли два отрезка (да/нет);
- ``point_in_polygon``    — лежит ли точка внутри многоугольника (да/нет);
- ``closest_pair``        — расстояние между ближайшей парой точек (2 знака).

Все координаты целые; эталон вычисляется точными предикатами ориентации.
"""

import math
import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def _cross(o: Point, a: Point, b: Point) -> int:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: List[Point]) -> List[Point]:
    """Оболочка по алгоритму Эндрю (без коллинеарных точек на рёбрах)."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    lower: List[Point] = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: List[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _on_segment(p: Point, q: Point, r: Point) -> bool:
    """r лежит на отрезке pq (при коллинеарности)."""
    return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and
            min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    d1 = _cross(c, d, a)
    d2 = _cross(c, d, b)
    d3 = _cross(a, b, c)
    d4 = _cross(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return True
    if d1 == 0 and _on_segment(c, d, a):
        return True
    if d2 == 0 and _on_segment(c, d, b):
        return True
    if d3 == 0 and _on_segment(a, b, c):
        return True
    if d4 == 0 and _on_segment(a, b, d):
        return True
    return False


def point_in_polygon(poly: List[Point], pt: Point) -> bool:
    """Луч вправо (ray casting). Точки на границе исключены при генерации."""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside


class ComputationalGeometryTask(BaseMathTask):
    TASK_TYPE = "computational_geometry"
    TASK_TYPES = ["convex_hull", "segment_intersection", "point_in_polygon", "closest_pair"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "coord": 6}, 2: {"n": 6, "coord": 7}, 3: {"n": 7, "coord": 8},
        4: {"n": 8, "coord": 9}, 5: {"n": 9, "coord": 10}, 6: {"n": 10, "coord": 12},
        7: {"n": 12, "coord": 13}, 8: {"n": 14, "coord": 15}, 9: {"n": 16, "coord": 17},
        10: {"n": 18, "coord": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.coord = int(p["coord"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rand_points(self, k: int) -> List[Point]:
        c = self.coord
        pts = set()
        while len(pts) < k:
            pts.add((random.randint(-c, c), random.randint(-c, c)))
        return list(pts)

    def _build(self):
        if self.task_type == "convex_hull":
            while True:
                self.points = self._rand_points(self.n)
                self.hull = convex_hull(self.points)
                if len(self.hull) >= 3:
                    break
            self.answer = len(self.hull)
        elif self.task_type == "segment_intersection":
            while True:
                p = self._rand_points(4)
                self.seg = (p[0], p[1], p[2], p[3])
                # исключаем совпадающие концы
                if len({p[0], p[1]}) == 2 and len({p[2], p[3]}) == 2:
                    break
            self.answer = segments_intersect(*self.seg)
        elif self.task_type == "point_in_polygon":
            while True:
                base = self._rand_points(max(5, self.n))
                self.poly = convex_hull(base)
                if len(self.poly) >= 3:
                    break
            c = self.coord
            while True:
                pt = (random.randint(-c, c), random.randint(-c, c))
                if self._strictly_off_boundary(pt):
                    self.query = pt
                    break
            self.answer = point_in_polygon(self.poly, self.query)
        else:  # closest_pair
            self.points = self._rand_points(self.n)
            best = min(math.dist(a, b)
                       for i, a in enumerate(self.points)
                       for b in self.points[i + 1:])
            self.dist = best
            self.answer = round(best, 2)

    def _strictly_off_boundary(self, pt: Point) -> bool:
        poly = self.poly
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if _cross(a, b, pt) == 0 and _on_segment(a, b, pt):
                return False
        return True

    @staticmethod
    def _pts_str(pts: List[Point]) -> str:
        return ", ".join(f"({x},{y})" for x, y in pts)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "convex_hull":
            return ((f"Даны точки на плоскости: {self._pts_str(self.points)}. Сколько вершин у их "
                     f"выпуклой оболочки? (точки, лежащие внутри ребра, вершинами не считаются)") if ru else
                    (f"Given points on the plane: {self._pts_str(self.points)}. How many vertices "
                     f"does their convex hull have? (points lying on an edge do not count)"))
        if self.task_type == "segment_intersection":
            a, b, c, d = self.seg
            return ((f"Отрезок 1: {a}–{b}. Отрезок 2: {c}–{d}. Пересекаются ли эти два отрезка "
                     f"(включая касание)? Ответьте да/нет.") if ru else
                    (f"Segment 1: {a}–{b}. Segment 2: {c}–{d}. Do these two segments intersect "
                     f"(touching counts)? Answer yes/no."))
        if self.task_type == "point_in_polygon":
            return ((f"Многоугольник задан вершинами по порядку: {self._pts_str(self.poly)}. Лежит "
                     f"ли точка {self.query} строго внутри него? Ответьте да/нет.") if ru else
                    (f"A polygon is given by its vertices in order: {self._pts_str(self.poly)}. Is "
                     f"the point {self.query} strictly inside it? Answer yes/no."))
        return ((f"Даны точки: {self._pts_str(self.points)}. Найдите расстояние между ближайшей "
                 f"парой точек (округлите до 2 знаков).") if ru else
                (f"Given points: {self._pts_str(self.points)}. Find the distance between the closest "
                 f"pair of points (round to 2 decimals)."))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "convex_hull":
            step = ("Строим оболочку (обход Эндрю) и считаем вершины-повороты." if ru else
                    "Build the hull (Andrew's monotone chain) and count the turn vertices.")
            self.final_answer = str(self.answer)
        elif self.task_type == "segment_intersection":
            step = ("Сравниваем ориентации концов относительно другого отрезка (предикат CCW)." if ru
                    else "Compare orientations of endpoints w.r.t. the other segment (CCW test).")
            self.final_answer = ("да" if self.answer else "нет") if ru else ("yes" if self.answer else "no")
        elif self.task_type == "point_in_polygon":
            step = ("Пускаем луч вправо и считаем пересечения со сторонами (чётность)." if ru else
                    "Cast a ray to the right and count crossings with the sides (parity).")
            self.final_answer = ("да" if self.answer else "нет") if ru else ("yes" if self.answer else "no")
        else:
            step = ("Перебираем все пары и берём минимум евклидовых расстояний." if ru else
                    "Check all pairs and take the minimum Euclidean distance.")
            self.final_answer = f"{self.answer:.2f}"
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "convex_hull":
            return U.verify_int(prediction, int(self.answer))
        if self.task_type == "closest_pair":
            return U.verify_value(prediction, float(self.dist), tol=1e-2)
        return U.verify_bool(prediction, bool(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3,
                             difficulty=5, reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
