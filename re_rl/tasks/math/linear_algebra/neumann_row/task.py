"""NeumannRowTask — частичная сумма геометрического ряда матрицы.

Следующий член равен матрице на предыдущий, а единичная минус матрица, умноженная на сумму, равна единичной минус следующему члену.
Степень обрезки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

State = Tuple[int, int, int, int, int, int, int, int]


def _apply(a: int, b: int, c: int, d: int, m00: int, m01: int, m10: int, m11: int) -> Tuple[int, int, int, int]:
    return (
        a * m00 + b * m10,
        a * m01 + b * m11,
        c * m00 + d * m10,
        c * m01 + d * m11,
    )


def neumann_trace(a: int, b: int, c: int, d: int, degree: int) -> List[State]:
    if degree < 0:
        raise RuntimeError("sum mismatch")
    term = (1, 0, 0, 1)
    total = term
    trace = [term + total]
    for _k in range(1, degree + 1):
        term = _apply(a, b, c, d, *term)
        total = tuple(left + right for left, right in zip(total, term))
        trace.append(term + total)
    nxt = _apply(a, b, c, d, *term)
    s00, s01, s10, s11 = total
    left = (
        (1 - a) * s00 - b * s10,
        (1 - a) * s01 - b * s11,
        -c * s00 + (1 - d) * s10,
        -c * s01 + (1 - d) * s11,
    )
    right = (1 - nxt[0], -nxt[1], -nxt[2], 1 - nxt[3])
    if left != right:
        raise RuntimeError("sum mismatch")
    return trace


class NeumannRowTask(BaseMathTask):
    TASK_TYPE = "neumann_row"
    TASK_TYPES = ["entry", "tr"]

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
        self.n = max(1, int(p["n"]))
        self.a = random.randint(-1, 1)
        self.b = random.randint(-1, 1)
        self.c = random.randint(-1, 1)
        self.d = random.randint(-1, 1)
        self.trace = neumann_trace(self.a, self.b, self.c, self.d, self.n)
        self.entry = self.trace[-1][4]
        self.tr = self.trace[-1][4] + self.trace[-1][7]
        self.answer = self.entry if self.task_type == "entry" else self.tr
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, a=self.a, b=self.b, c=self.c, d=self.d)

    def solve(self):
        steps = []
        for index, row in enumerate(self.trace):
            payload = dict(
                t00=row[0], t01=row[1], t10=row[2], t11=row[3],
                s00=row[4], s01=row[5], s10=row[6], s11=row[7],
            )
            if index == 0:
                steps.append(texts.t("s2", self.language, **payload))
            else:
                steps.append(texts.t("s3", self.language, k=index, **payload))
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
