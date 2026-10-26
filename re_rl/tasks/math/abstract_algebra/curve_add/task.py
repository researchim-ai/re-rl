"""CurveAddTask — сложение точки с собой на эллиптической кривой.

Каждое сложение — хорда или касательная над простым полем. Число сложений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Optional[Tuple[int, int]]


def _inverse(value: int, prime: int) -> int:
    value %= prime
    old_r, r = prime, value
    old_s, s = 0, 1
    while r:
        quot = old_r // r
        old_r, r = r, old_r - quot * r
        old_s, s = s, old_s - quot * s
    if old_r != 1:
        raise RuntimeError("curve mismatch")
    return old_s % prime


def _add(first: Point, second: Point, coeff: int, prime: int) -> Point:
    if first is None:
        return second
    if second is None:
        return first
    x1, y1 = first
    x2, y2 = second
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if first == second:
        slope = (3 * x1 * x1 + coeff) * _inverse(2 * y1, prime) % prime
    else:
        slope = (y2 - y1) * _inverse(x2 - x1, prime) % prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    return x3, y3


def _on_curve(point: Point, coeff: int, shift: int, prime: int) -> bool:
    if point is None:
        return True
    x_coord, y_coord = point
    return (y_coord * y_coord - (x_coord ** 3 + coeff * x_coord + shift)) % prime == 0


def curve_trace(coeff: int, shift: int, prime: int, px: int, py: int, steps: int) -> List[Tuple[int, int, int]]:
    base = (px % prime, py % prime)
    disc = (-16 * (4 * coeff ** 3 + 27 * shift * shift)) % prime
    if disc == 0 or not _on_curve(base, coeff, shift, prime):
        raise RuntimeError("curve mismatch")
    opposite = (base[0], (-base[1]) % prime)
    if _add(base, opposite, coeff, prime) is not None:
        raise RuntimeError("curve mismatch")
    current: Point = None
    visits = 0
    trace = []
    for _ in range(steps):
        current = _add(current, base, coeff, prime)
        if not _on_curve(current, coeff, shift, prime):
            raise RuntimeError("curve mismatch")
        if current is None:
            visits += 1
            trace.append((prime, prime, visits))
        else:
            trace.append((current[0], current[1], visits))
    return trace


class CurveAddTask(BaseMathTask):
    TASK_TYPE = "curve_add"
    TASK_TYPES = ["abscissa", "visits"]
    PRIMES = (11, 13, 17, 19, 23)

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
        self.prime = self.coeff = self.shift = self.px = self.py = 0
        self.trace: List[Tuple[int, int, int]] = []
        for _ in range(200):
            prime = random.choice(self.PRIMES)
            coeff = random.randrange(prime)
            shift = random.randrange(prime)
            if (-16 * (4 * coeff ** 3 + 27 * shift * shift)) % prime == 0:
                continue
            usable = []
            for x_coord in range(prime):
                rhs = (x_coord ** 3 + coeff * x_coord + shift) % prime
                for y_coord in range(1, prime):
                    if (y_coord * y_coord) % prime == rhs:
                        usable.append((x_coord, y_coord))
            if not usable:
                continue
            self.prime = prime
            self.coeff = coeff
            self.shift = shift
            self.px, self.py = random.choice(usable)
            self.trace = curve_trace(coeff, shift, prime, self.px, self.py, self.n)
            break
        if not self.trace:
            raise RuntimeError("curve mismatch")
        self.abscissa = self.trace[-1][0]
        self.visits = self.trace[-1][2]
        self.answer = self.abscissa if self.task_type == "abscissa" else self.visits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "abscissa" else "s1"
        return texts.t(
            key, language, n=self.n, prime=self.prime, coeff=self.coeff, shift=self.shift,
            px=self.px, py=self.py,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, x=x_coord, y=y_coord, visits=visits)
            for index, (x_coord, y_coord, visits) in enumerate(self.trace, 1)
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
