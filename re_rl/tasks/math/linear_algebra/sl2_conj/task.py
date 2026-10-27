"""Sl2ConjTask — сопряжение матрицы цепочкой сдвигов.

Каждый сдвиг заменяется на обратный, умноженный на матрицу, умноженный на сам сдвиг. След и определитель не меняются.
Число сдвигов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

State = Tuple[int, int, int, int, int]


def shear_trace(a: int, b: int, c: int, d: int, shifts: Sequence[int]) -> List[State]:
    if not shifts:
        raise RuntimeError("shear mismatch")
    trace_sum = a + d
    det = a * d - b * c
    trace = []
    for shift in shifts:
        right00, right01 = a, a * shift + b
        right10, right11 = c, c * shift + d
        a = right00 - shift * right10
        b = right01 - shift * right11
        c = right10
        d = right11
        if a + d != trace_sum or a * d - b * c != det:
            raise RuntimeError("shear mismatch")
        trace.append((a, b, c, d, det))
    return trace


class Sl2ConjTask(BaseMathTask):
    TASK_TYPE = "sl2_conj"
    TASK_TYPES = ["corner", "det"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.a = random.randint(-2, 2)
        self.b = random.randint(-2, 2)
        self.c = random.randint(-2, 2)
        self.d = random.randint(-2, 2)
        self.shifts = [random.choice((-2, -1, 1, 2)) for _ in range(self.n)]
        self.trace = shear_trace(self.a, self.b, self.c, self.d, self.shifts)
        self.corner = self.trace[-1][1]
        self.det = self.trace[-1][4]
        self.answer = self.corner if self.task_type == "corner" else self.det
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shifts(self) -> str:
        return " ".join(str(shift) for shift in self.shifts)

    def _descr(self, language):
        key = "s0" if self.task_type == "corner" else "s1"
        return texts.t(
            key, language, n=self.n, a=self.a, b=self.b, c=self.c, d=self.d, shifts=self._shifts(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, k=shift, a=a, b=b, c=c, d=d, det=det)
            for index, ((a, b, c, d, det), shift) in enumerate(zip(self.trace, self.shifts), 1)
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
