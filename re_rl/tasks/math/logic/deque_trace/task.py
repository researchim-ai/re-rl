"""DequeTraceTask — операции с двухсторонней очередью.

L и R кладут число слева или справа. l и r снимают слева или справа.
Пустая очередь не снимается. Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple


def deque_trace(ops: Sequence[Op]) -> List[Tuple[int, int]]:
    items = []
    trace = []
    for op in ops:
        kind = op[0]
        if kind == "L":
            items.insert(0, op[1])
        elif kind == "R":
            items.append(op[1])
        elif kind == "l":
            items.pop(0)
        else:
            items.pop()
        front = items[0] if items else 0
        trace.append((front, len(items)))
    return trace


class DequeTraceTask(BaseMathTask):
    TASK_TYPE = "deque_trace"
    TASK_TYPES = ["front", "size"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 11},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.ops = []
        size = 0
        for _ in range(self.n):
            if size == 0 or random.randint(0, 2) > 0:
                value = random.randint(1, 9)
                kind = random.choice(("L", "R"))
                self.ops.append((kind, value))
                size += 1
            else:
                kind = random.choice(("l", "r"))
                self.ops.append((kind,))
                size -= 1
        self.trace = deque_trace(self.ops)
        self.front, self.size = self.trace[-1]
        self.answer = self.front if self.task_type == "front" else self.size
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _op_text(self, op: Op) -> str:
        if op[0] in ("L", "R"):
            return f"{op[0]}{op[1]}"
        return op[0]

    def _descr(self, language):
        listing = ", ".join(self._op_text(op) for op in self.ops)
        key = "s0" if self.task_type == "front" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=self._op_text(op), front=front, size=size)
            for index, (op, (front, size)) in enumerate(zip(self.ops, self.trace), 1)
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
