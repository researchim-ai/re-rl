"""FormReduceTask — приведение положительной бинарной квадратичной формы.

Шаг заменяет b ближайшим целым сдвигом и при необходимости меняет концы местами.
Число форм растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _nearest(numer: int, denom: int) -> int:
    quot = Fraction(numer, denom)
    magnitude = math.floor(abs(quot) + Fraction(1, 2))
    if quot < 0:
        return -magnitude
    return magnitude


def _reduce_one(coeff_a: int, coeff_b: int, coeff_c: int) -> Tuple[int, int, int]:
    disc = coeff_b * coeff_b - 4 * coeff_a * coeff_c
    if coeff_a <= 0 or disc >= 0:
        raise RuntimeError("form mismatch")
    seen = set()
    for _ in range(64):
        reduced = abs(coeff_b) <= coeff_a <= coeff_c and not (
            (abs(coeff_b) == coeff_a or coeff_a == coeff_c) and coeff_b < 0
        )
        if reduced:
            if coeff_b * coeff_b - 4 * coeff_a * coeff_c != disc or coeff_c <= 0:
                raise RuntimeError("form mismatch")
            return coeff_a, coeff_b, coeff_c
        key = (coeff_a, coeff_b, coeff_c)
        if key in seen:
            raise RuntimeError("form mismatch")
        seen.add(key)
        quot = _nearest(coeff_b, 2 * coeff_a)
        coeff_b = coeff_b - 2 * quot * coeff_a
        numer = coeff_b * coeff_b - disc
        if numer % (4 * coeff_a) != 0:
            raise RuntimeError("form mismatch")
        coeff_c = numer // (4 * coeff_a)
        if coeff_a > coeff_c or (coeff_a == coeff_c and coeff_b < 0):
            coeff_a, coeff_b, coeff_c = coeff_c, -coeff_b, coeff_a
    raise RuntimeError("form mismatch")


def form_trace(forms: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    total = 0
    trace = []
    for coeff_a, coeff_b, coeff_c in forms:
        lead, middle, _tail = _reduce_one(coeff_a, coeff_b, coeff_c)
        total += lead
        trace.append((lead, middle, total))
    return trace


class FormReduceTask(BaseMathTask):
    TASK_TYPE = "form_reduce"
    TASK_TYPES = ["lead", "total"]

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
        self.forms: List[Tuple[int, int, int]] = []
        while len(self.forms) < self.n:
            coeff_a = random.randint(1, 8)
            coeff_b = random.randint(-16, 16)
            coeff_c = random.randint(1, 12)
            if coeff_b * coeff_b - 4 * coeff_a * coeff_c < 0:
                self.forms.append((coeff_a, coeff_b, coeff_c))
        self.trace = form_trace(self.forms)
        self.lead = self.trace[-1][0]
        self.total = self.trace[-1][2]
        self.answer = self.lead if self.task_type == "lead" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        parts = ["(%d, %d, %d)" % triple for triple in self.forms]
        return "; ".join(parts)

    def _descr(self, language):
        key = "s0" if self.task_type == "lead" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, lead=lead, middle=middle, total=total)
            for index, (lead, middle, total) in enumerate(self.trace, 1)
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
