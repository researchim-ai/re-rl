"""PostIncTask — постфиксное и префиксное увеличение.

Код 0 сначала отдаёт старое значение, потом прибавляет 1. Код 1 сначала прибавляет 1, потом отдаёт новое.
Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def post_trace(start: int, ops: Sequence[int]) -> List[Tuple[int, int]]:
    value = start
    used = 0
    trace = []
    for op in ops:
        if op == 0:
            used += value
            value += 1
        else:
            value += 1
            used += value
        trace.append((value, used))
    return trace


class PostIncTask(BaseMathTask):
    TASK_TYPE = "post_inc"
    TASK_TYPES = ["value", "used"]

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
        self.start = random.randint(0, 5)
        self.ops = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = post_trace(self.start, self.ops)
        self.value = self.trace[-1][0]
        self.used = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.used
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(op) for op in self.ops)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=op, value=value, used=used)
            for index, (op, (value, used)) in enumerate(zip(self.ops, self.trace), 1)
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
