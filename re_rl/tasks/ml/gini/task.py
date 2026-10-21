"""GiniSplitTask — прирост чистоты по критерию Джини (CART).

Джини G = 1 - sum (c/n)^2 = (n^2 - sum c^2) / n^2 — точная дробь при любых
целых кратностях. Прирост = G(родитель) - (nL/n) G(лево) - (nR/n) G(право).

Подтипы:
- ``gain``         — прирост Джини одного бинарного признака;
- ``best_feature`` — какой из двух признаков даёт больший прирост (A или B).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Row = Tuple[int, int, int]  # y, fA, fB


def gini(counts: Sequence[int]) -> Fraction:
    n = sum(counts)
    if n == 0:
        return Fraction(0)
    return Fraction(n * n - sum(c * c for c in counts), n * n)


def class_counts(rows: Sequence[Row], pred) -> Tuple[int, int]:
    neg = sum(1 for row in rows if row[0] == 0 and pred(row))
    pos = sum(1 for row in rows if row[0] == 1 and pred(row))
    return neg, pos


def gini_gain(rows: Sequence[Row], feature: int) -> Fraction:
    """feature: 1 для fA, 2 для fB."""
    parent = class_counts(rows, lambda r: True)
    left = class_counts(rows, lambda r: r[feature] == 0)
    right = class_counts(rows, lambda r: r[feature] == 1)
    n, nl, nr = sum(parent), sum(left), sum(right)
    if n == 0 or nl == 0 or nr == 0:
        return Fraction(0)
    return gini(parent) - Fraction(nl, n) * gini(left) - Fraction(nr, n) * gini(right)


class GiniSplitTask(BaseMathTask):
    TASK_TYPE = "gini_split"
    TASK_TYPES = ["gain", "best_feature"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 6}, 5: {"n": 8},
        6: {"n": 8}, 7: {"n": 10}, 8: {"n": 10}, 9: {"n": 12}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _sample_rows(self) -> List[Row]:
        rows = []
        for _ in range(self.n):
            rows.append((random.randint(0, 1), random.randint(0, 1), random.randint(0, 1)))
        return rows

    def _build(self):
        self.rows = self._sample_rows()
        self.gain_a = gini_gain(self.rows, 1)
        self.gain_b = gini_gain(self.rows, 2)
        if self.task_type == "best_feature":
            for _ in range(40):
                if self.gain_a != self.gain_b and min(self.gain_a, self.gain_b) >= 0:
                    break
                self.rows = self._sample_rows()
                self.gain_a = gini_gain(self.rows, 1)
                self.gain_b = gini_gain(self.rows, 2)
            if self.gain_a == self.gain_b:
                # Учебный разрез: A идеально отделяет классы, B постоянен.
                half = self.n // 2
                self.rows = [(0, 0, 0) for _ in range(half)] + [(1, 1, 0) for _ in range(self.n - half)]
                self.gain_a = gini_gain(self.rows, 1)
                self.gain_b = gini_gain(self.rows, 2)
            self.answer_label = "A" if self.gain_a > self.gain_b else "B"
        else:
            self.answer_frac = self.gain_a

    def _table(self) -> str:
        lines = ["y fA fB"]
        for y, a, b in self.rows:
            lines.append(f"{y} {a} {b}")
        return "\n".join(lines)

    def _descr(self, language):
        table = self._table()
        rule = ((texts.t('s0', language)))
        if self.task_type == "gain":
            ask = ((texts.t('s1', language, table=table)))
        else:
            ask = ((texts.t('s2', language, table=table)))
        return f"{rule}\n{ask}"

    def solve(self):
        if self.task_type == "gain":
            shown = fmt_fraction(self.gain_a)
            step = ((texts.t('s3', self.language, shown=shown)))
            self.final_answer = shown
        else:
            step = ((texts.t('s4', self.language, v0=fmt_fraction(self.gain_a), v1=fmt_fraction(self.gain_b))))
            self.final_answer = self.answer_label
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.final_answer)))]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "best_feature":
            return U.verify_label(prediction, [self.answer_label])
        return verify_fraction(prediction, self.gain_a)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
