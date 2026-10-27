"""BidiagSolveTask — решение двухдиагональной системы прямой подстановкой.

Каждая неизвестная равна числителю, делённому нацело на диагональный элемент.
Число неизвестных растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def bidiag_trace(diag: Sequence[int], sub: Sequence[int], rhs: Sequence[int]) -> List[Tuple[int, int]]:
    width = len(diag)
    if width < 1 or len(rhs) != width or len(sub) != width - 1:
        raise RuntimeError("solve mismatch")
    values = []
    trace = []
    for index, pivot in enumerate(diag):
        if pivot == 0:
            raise RuntimeError("solve mismatch")
        numer = rhs[index] if index == 0 else rhs[index] - sub[index - 1] * values[-1]
        if numer % pivot != 0:
            raise RuntimeError("solve mismatch")
        value = numer // pivot
        values.append(value)
        trace.append((value, numer))
    if diag[0] * values[0] != rhs[0]:
        raise RuntimeError("solve mismatch")
    for index in range(1, width):
        if sub[index - 1] * values[index - 1] + diag[index] * values[index] != rhs[index]:
            raise RuntimeError("solve mismatch")
    return trace


class BidiagSolveTask(BaseMathTask):
    TASK_TYPE = "bidiag_solve"
    TASK_TYPES = ["tail", "total"]

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
        self.diag = [random.choice((-2, -1, 1, 2)) for _ in range(self.n)]
        self.sub = [random.randint(-3, 3) for _ in range(self.n - 1)]
        planted = [random.randint(-3, 3) for _ in range(self.n)]
        self.rhs = [self.diag[0] * planted[0]]
        for index in range(1, self.n):
            self.rhs.append(self.sub[index - 1] * planted[index - 1] + self.diag[index] * planted[index])
        self.trace = bidiag_trace(self.diag, self.sub, self.rhs)
        self.tail = self.trace[-1][0]
        self.total = sum(value for value, _numer in self.trace)
        self.answer = self.tail if self.task_type == "tail" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _nums(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "tail" else "s1"
        return texts.t(
            key, language, n=self.n, diag=self._nums(self.diag),
            sub=self._nums(self.sub), rhs=self._nums(self.rhs),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, val=val, num=num)
            for index, (val, num) in enumerate(self.trace, 1)
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
