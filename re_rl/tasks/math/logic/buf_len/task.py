"""BufLenTask — длина буфера после дописывания и стирания.

Код 0 дописывает указанное число символов. Код 1 стирает не больше, чем есть, и длина не падает ниже нуля.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def buf_trace(ops: Sequence[Op]) -> List[Tuple[int, int]]:
    length = 0
    peak = 0
    trace = []
    for kind, amount in ops:
        if kind == 0:
            length += amount
        else:
            length = max(0, length - amount)
        peak = max(peak, length)
        trace.append((length, peak))
    return trace


class BufLenTask(BaseMathTask):
    TASK_TYPE = "buf_len"
    TASK_TYPES = ["length", "peak"]

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
        self.ops = [(random.randint(0, 1), random.randint(1, 4)) for _ in range(self.n)]
        self.trace = buf_trace(self.ops)
        self.length = self.trace[-1][0]
        self.peak = self.trace[-1][1]
        self.answer = self.length if self.task_type == "length" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{kind} {amount}" for kind, amount in self.ops)
        key = "s0" if self.task_type == "length" else "s1"
        return texts.t(key, language, n=self.n, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kind=kind, amount=amount, length=length, peak=peak)
            for index, ((kind, amount), (length, peak)) in enumerate(zip(self.ops, self.trace), 1)
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
