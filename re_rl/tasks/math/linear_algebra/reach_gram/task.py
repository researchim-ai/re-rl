"""ReachGramTask — конечный грамиан достижимости.

Каждый шаг заменяет накопитель на A W A^T плюс внешний квадрат входного вектора.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Mat = Tuple[int, int, int, int]


def reach_trace(a: int, b: int, c: int, d: int, q1: int, q2: int, steps: int) -> List[Mat]:
    if steps < 0:
        raise RuntimeError("reach mismatch")
    q00 = q1 * q1
    q01 = q1 * q2
    q11 = q2 * q2
    w00, w01, w10, w11 = q00, q01, q01, q11
    trace = [(w00, w01, w10, w11)]
    for _ in range(steps):
        aw00 = a * w00 + b * w10
        aw01 = a * w01 + b * w11
        aw10 = c * w00 + d * w10
        aw11 = c * w01 + d * w11
        w00 = aw00 * a + aw01 * b + q00
        w01 = aw00 * c + aw01 * d + q01
        w10 = aw10 * a + aw11 * b + q01
        w11 = aw10 * c + aw11 * d + q11
        if w01 != w10:
            raise RuntimeError("reach mismatch")
        trace.append((w00, w01, w10, w11))
    vx, vy = q1, q2
    acc = (q00, q01, q01, q11)
    for _ in range(steps):
        vx, vy = a * vx + b * vy, c * vx + d * vy
        acc = (acc[0] + vx * vx, acc[1] + vx * vy, acc[2] + vx * vy, acc[3] + vy * vy)
    if acc != trace[-1]:
        raise RuntimeError("reach mismatch")
    return trace


class ReachGramTask(BaseMathTask):
    TASK_TYPE = "reach_gram"
    TASK_TYPES = ["entry", "tr"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
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
        self.q1 = random.randint(-2, 2)
        self.q2 = random.randint(-2, 2)
        self.trace = reach_trace(self.a, self.b, self.c, self.d, self.q1, self.q2, self.n)
        self.entry = self.trace[-1][0]
        self.tr = self.trace[-1][0] + self.trace[-1][3]
        self.answer = self.entry if self.task_type == "entry" else self.tr
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(
            key, language, n=self.n, a=self.a, b=self.b, c=self.c, d=self.d, q1=self.q1, q2=self.q2,
        )

    def solve(self):
        steps = []
        for index, (w00, w01, w10, w11) in enumerate(self.trace):
            if index == 0:
                steps.append(texts.t("s2", self.language, w00=w00, w01=w01, w10=w10, w11=w11))
            else:
                steps.append(texts.t("s3", self.language, k=index, w00=w00, w01=w01, w10=w10, w11=w11))
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
