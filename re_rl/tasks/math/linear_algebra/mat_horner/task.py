"""MatHornerTask — значение многочлена от матрицы схемой Горнера.

Накопитель умножается на матрицу, и следующий коэффициент прибавляется к диагонали.
Степень многочлена растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Mat = Tuple[int, int, int, int]


def _apply(a: int, b: int, c: int, d: int, m00: int, m01: int, m10: int, m11: int) -> Mat:
    return (
        a * m00 + b * m10,
        a * m01 + b * m11,
        c * m00 + d * m10,
        c * m01 + d * m11,
    )


def horner_apply(a: int, b: int, c: int, d: int, coefs: Sequence[int]) -> List[Mat]:
    if len(coefs) < 2:
        raise RuntimeError("poly mismatch")
    acc = (coefs[0], 0, 0, coefs[0])
    trace = [acc]
    for coef in coefs[1:]:
        nxt = _apply(a, b, c, d, *acc)
        acc = (nxt[0] + coef, nxt[1], nxt[2], nxt[3] + coef)
        trace.append(acc)
    degree = len(coefs) - 1
    power = (1, 0, 0, 1)
    total = (coefs[degree], 0, 0, coefs[degree])
    for k in range(1, degree + 1):
        power = _apply(a, b, c, d, *power)
        coef = coefs[degree - k]
        total = tuple(left + coef * right for left, right in zip(total, power))
    if total != trace[-1]:
        raise RuntimeError("poly mismatch")
    return trace


class MatHornerTask(BaseMathTask):
    TASK_TYPE = "mat_horner"
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
        self.coefs = [random.randint(-2, 2) for _ in range(self.n + 1)]
        self.trace = horner_apply(self.a, self.b, self.c, self.d, self.coefs)
        self.entry = self.trace[-1][0]
        self.tr = self.trace[-1][0] + self.trace[-1][3]
        self.answer = self.entry if self.task_type == "entry" else self.tr
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _coefs(self) -> str:
        return " ".join(str(coef) for coef in self.coefs)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(
            key, language, n=self.n, count=self.n + 1, a=self.a, b=self.b, c=self.c, d=self.d,
            coefs=self._coefs(),
        )

    def solve(self):
        steps = [texts.t(
            "s2", self.language,
            p00=self.trace[0][0], p01=self.trace[0][1], p10=self.trace[0][2], p11=self.trace[0][3],
        )]
        for index, acc in enumerate(self.trace[1:], 1):
            steps.append(texts.t(
                "s3", self.language, k=index, coef=self.coefs[index],
                p00=acc[0], p01=acc[1], p10=acc[2], p11=acc[3],
            ))
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
