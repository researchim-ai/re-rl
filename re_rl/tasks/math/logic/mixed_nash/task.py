"""MixedNashTask — внутреннее смешанное равновесие игры 2×2.

p — вероятность верхней строки, которая делает столбца безразличным.
q — вероятность левого столбца, которая делает строку безразличной.
Генератор оставляет только игры, где обе вероятности строго между 0 и 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Matrix = Sequence[Sequence[int]]


def mixed_equilibrium(row: Matrix, column: Matrix) -> Optional[Tuple[Fraction, Fraction]]:
    a00, a01 = row[0]
    a10, a11 = row[1]
    b00, b01 = column[0]
    b10, b11 = column[1]
    den_p = b00 - b10 - b01 + b11
    den_q = a00 - a01 - a10 + a11
    if den_p == 0 or den_q == 0:
        return None
    row_prob = Fraction(b11 - b10, den_p)
    col_prob = Fraction(a11 - a01, den_q)
    if not (0 < row_prob < 1 and 0 < col_prob < 1):
        return None
    return row_prob, col_prob


class MixedNashTask(BaseMathTask):
    TASK_TYPE = "mixed_nash"
    TASK_TYPES = ["row", "column"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mag": 2}, 2: {"mag": 3}, 3: {"mag": 3}, 4: {"mag": 4}, 5: {"mag": 5},
        6: {"mag": 5}, 7: {"mag": 6}, 8: {"mag": 7}, 9: {"mag": 8}, 10: {"mag": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        found = None
        for _ in range(80):
            self.row = [[random.randint(-self.mag, self.mag) for _ in range(2)] for _ in range(2)]
            self.column = [[random.randint(-self.mag, self.mag) for _ in range(2)] for _ in range(2)]
            found = mixed_equilibrium(self.row, self.column)
            if found is not None:
                break
        if found is None:
            self.row = [[1, -1], [-1, 1]]
            self.column = [[-1, 1], [1, -1]]
            found = mixed_equilibrium(self.row, self.column)
        self.row_prob, self.col_prob = found
        self.answer = self.row_prob if self.task_type == "row" else self.col_prob
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _cells(self, matrix: List[List[int]], language: str) -> str:
        if {"ru": True, "en": False}.get(language, False):
            return (texts.t('s4', language, v0=matrix[0][0], v1=matrix[0][1], v2=matrix[1][0], v3=matrix[1][1]))
        return (texts.t('s3', language, v0=matrix[0][0], v1=matrix[0][1], v2=matrix[1][0], v3=matrix[1][1]))

    def _descr(self, language):
        rule = (
            texts.t('s0', language, v0=self._cells(self.row, language), v1=self._cells(self.column, language))
        )
        ask = texts.t('s1', language) if self.task_type == "row" else texts.t('s2', language)
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((f"p = {fmt_fraction(self.row_prob)}, q = {fmt_fraction(self.col_prob)}."))
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
