"""RationalRootTask — проверка целых кандидатов в корни.

Кандидат является корнем, если схема Горнера даёт ноль.
Число кандидатов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def horner_value(coeffs: Sequence[int], point: int) -> int:
    acc = 0
    for coeff in coeffs:
        acc = acc * point + coeff
    return acc


def root_trace(coeffs: Sequence[int], candidates: Sequence[int]) -> List[int]:
    return [horner_value(coeffs, point) for point in candidates]


class RationalRootTask(BaseMathTask):
    TASK_TYPE = "rational_root"
    TASK_TYPES = ["count", "small"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        root = random.randint(-4, 4)
        quad = [1, random.randint(-2, 2), random.randint(-2, 2)]
        # (x - root) * (x^2 + a x + b)
        linear = [1, -root]
        self.coeffs = [
            quad[0] * linear[0],
            quad[0] * linear[1] + quad[1] * linear[0],
            quad[1] * linear[1] + quad[2] * linear[0],
            quad[2] * linear[1],
        ]
        pool = [value for value in range(-6, 7) if value != root]
        random.shuffle(pool)
        self.candidates = sorted([root] + pool[: self.n - 1])
        self.values = root_trace(self.coeffs, self.candidates)
        symbol = sp.symbols("x")
        poly = sp.Poly(self.coeffs, symbol)
        for point, value in zip(self.candidates, self.values):
            assert int(poly.subs(symbol, point)) == value
        self.roots = [point for point, value in zip(self.candidates, self.values) if value == 0]
        self.count = len(self.roots)
        self.small = min(self.roots) if self.roots else 0
        self.answer = self.count if self.task_type == "count" else self.small
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        coeffs = ", ".join(str(coeff) for coeff in self.coeffs)
        listing = ", ".join(str(point) for point in self.candidates)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, coeffs=coeffs, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, point=point, value=value)
            for index, (point, value) in enumerate(zip(self.candidates, self.values), 1)
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
