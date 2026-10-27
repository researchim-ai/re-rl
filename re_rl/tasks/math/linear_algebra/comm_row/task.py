"""CommRowTask — цепочка коммутаторов матриц 2 на 2.

Каждый шаг заменяет матрицу на AX − XA, и след этого коммутатора равен нулю.
Число скобок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Mat = Tuple[int, int, int, int]


def commut_trace(mats: Sequence[Mat], start: Mat) -> List[Mat]:
    if not mats:
        raise RuntimeError("bracket mismatch")
    x00, x01, x10, x11 = start
    trace = []
    for a, b, c, d in mats:
        ax00 = a * x00 + b * x10
        ax01 = a * x01 + b * x11
        ax10 = c * x00 + d * x10
        ax11 = c * x01 + d * x11
        xa00 = x00 * a + x01 * c
        xa01 = x00 * b + x01 * d
        xa10 = x10 * a + x11 * c
        xa11 = x10 * b + x11 * d
        x00, x01, x10, x11 = ax00 - xa00, ax01 - xa01, ax10 - xa10, ax11 - xa11
        if x00 + x11 != 0:
            raise RuntimeError("bracket mismatch")
        trace.append((x00, x01, x10, x11))
    return trace


class CommRowTask(BaseMathTask):
    TASK_TYPE = "comm_row"
    TASK_TYPES = ["entry", "energy"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.start = tuple(random.randint(-2, 2) for _ in range(4))
        self.mats = [
            tuple(random.randint(-1, 1) for _ in range(4)) for _ in range(self.n)
        ]
        self.trace = commut_trace(self.mats, self.start)
        self.entry = self.trace[-1][0]
        last = self.trace[-1]
        self.energy = last[0] * last[0] + last[1] * last[1] + last[2] * last[2] + last[3] * last[3]
        self.answer = self.entry if self.task_type == "entry" else self.energy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{a} {b} {c} {d}" for a, b, c, d in self.mats)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        x00, x01, x10, x11 = self.start
        return texts.t(
            key, language, n=self.n, listing=self._listing(),
            x00=x00, x01=x01, x10=x10, x11=x11,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, x00=x00, x01=x01, x10=x10, x11=x11)
            for index, (x00, x01, x10, x11) in enumerate(self.trace, 1)
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
