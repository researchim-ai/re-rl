"""RegSwapTask — две переменные и постоянное слагаемое.

Код 0 меняет переменные местами. Код 1 прибавляет вторую к первой. Код 2 прибавляет постоянное слагаемое ко второй.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def reg_trace(left: int, right: int, extra: int, ops: Sequence[int]) -> List[Tuple[int, int, int]]:
    swaps = 0
    trace = []
    for op in ops:
        if op == 0:
            left, right = right, left
            swaps += 1
        elif op == 1:
            left = left + right
        else:
            right = right + extra
        trace.append((left, right, swaps))
    return trace


class RegSwapTask(BaseMathTask):
    TASK_TYPE = "reg_swap"
    TASK_TYPES = ["left", "swaps"]

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
        self.left = random.randint(0, 4)
        self.right = random.randint(0, 4)
        self.extra = random.randint(-2, 2)
        self.ops = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = reg_trace(self.left, self.right, self.extra, self.ops)
        self.final_left = self.trace[-1][0]
        self.swaps = self.trace[-1][2]
        self.answer = self.final_left if self.task_type == "left" else self.swaps
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(op) for op in self.ops)
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(
            key, language, n=self.n, left=self.left, right=self.right, extra=self.extra, ops=shown,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=op, left=left, right=right, swaps=swaps)
            for index, (op, (left, right, swaps)) in enumerate(zip(self.ops, self.trace), 1)
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
