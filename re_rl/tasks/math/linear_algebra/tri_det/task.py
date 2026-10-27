"""TriDetTask — определитель симметричной трёхдиагональной матрицы.

Каждый следующий главный минор равен диагональному элементу, умноженному на предыдущий минор, минус квадрат бокового элемента, умноженный на минор ещё раньше.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _gauss_det(diag: Sequence[int], off: Sequence[int]) -> int:
    main = [Fraction(item) for item in diag]
    side = [Fraction(item) for item in off]
    value = Fraction(1)
    for index, pivot in enumerate(main):
        if pivot == 0:
            raise RuntimeError("det mismatch")
        value *= pivot
        if index + 1 < len(main):
            main[index + 1] -= side[index] * side[index] / pivot
    if value.denominator != 1:
        raise RuntimeError("det mismatch")
    return int(value)


def tri_trace(diag: Sequence[int], off: Sequence[int]) -> List[Tuple[int, int]]:
    if len(off) != len(diag) - 1 or not diag:
        raise RuntimeError("det mismatch")
    older = 0
    previous = 1
    trace = []
    for index, item in enumerate(diag):
        value = item * previous - (off[index - 1] ** 2 * older if index else 0)
        trace.append((value, previous))
        older, previous = previous, value
    if value != _gauss_det(diag, off):
        raise RuntimeError("det mismatch")
    return trace


class TriDetTask(BaseMathTask):
    TASK_TYPE = "tri_det"
    TASK_TYPES = ["det", "prev"]

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
        self.off = [random.randint(1, 3) for _ in range(self.n - 1)]
        self.diag = []
        for index in range(self.n):
            left = self.off[index - 1] if index else 0
            right = self.off[index] if index + 1 < self.n else 0
            self.diag.append(left + right + random.randint(1, 3))
        self.trace = tri_trace(self.diag, self.off)
        self.det = self.trace[-1][0]
        self.prev = self.trace[-1][1]
        self.answer = self.det if self.task_type == "det" else self.prev
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _diag_listing(self) -> str:
        return " ".join(str(item) for item in self.diag)

    def _off_listing(self) -> str:
        return " ".join(str(item) for item in self.off)

    def _descr(self, language):
        key = "s0" if self.task_type == "det" else "s1"
        return texts.t(
            key, language, n=self.n, diag=self._diag_listing(), off=self._off_listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, det=det, prev=prev)
            for index, (det, prev) in enumerate(self.trace, 1)
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
