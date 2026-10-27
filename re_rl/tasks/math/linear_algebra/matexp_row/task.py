"""MatexpRowTask — усечённая матричная экспонента, домноженная на факториал.

Член следующей степени равен матрице на предыдущий член, делённый нацело на номер степени.
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


def matexp_trace(a: int, b: int, c: int, d: int, degree: int) -> List[State]:
    if degree < 1:
        raise RuntimeError("exp mismatch")
    scale = 1
    for k in range(1, degree + 1):
        scale *= k
    term = (scale, 0, 0, scale)
    total = term
    power = (1, 0, 0, 1)
    trace = [term + total]
    for k in range(1, degree + 1):
        raw = _apply(a, b, c, d, *term)
        if any(value % k != 0 for value in raw):
            raise RuntimeError("exp mismatch")
        term = tuple(value // k for value in raw)
        total = tuple(left + right for left, right in zip(total, term))
        power = _apply(a, b, c, d, *power)
        scale //= k
        powered = tuple(value * scale for value in power)
        if powered != term or tuple(left + right for left, right in zip(trace[-1][4:], term)) != total:
            raise RuntimeError("exp mismatch")
        trace.append(term + total)
    return trace


class MatexpRowTask(BaseMathTask):
    TASK_TYPE = "matexp_row"
    TASK_TYPES = ["entry", "tr"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
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
        self.trace = matexp_trace(self.a, self.b, self.c, self.d, self.n)
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
