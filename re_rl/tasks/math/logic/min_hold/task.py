"""MinHoldTask — стек и минимум лежащих чисел.

Код 0 кладёт число. Код 1 снимает верх, если стек не пуст. Минимум пустого стека равен 0.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def stack_min(ops: Sequence[Op]) -> List[Tuple[int, int]]:
    stack: List[int] = []
    popped = 0
    trace = []
    for kind, value in ops:
        if kind == 0:
            stack.append(value)
        elif stack:
            popped += stack.pop()
        low = min(stack) if stack else 0
        trace.append((low, popped))
    return trace


class MinHoldTask(BaseMathTask):
    TASK_TYPE = "min_hold"
    TASK_TYPES = ["low", "popped"]

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
        self.ops = []
        for _ in range(self.n):
            kind = random.randint(0, 1)
            value = random.randint(1, 9) if kind == 0 else 0
            self.ops.append((kind, value))
        self.trace = stack_min(self.ops)
        self.low = self.trace[-1][0]
        self.popped = self.trace[-1][1]
        self.answer = self.low if self.task_type == "low" else self.popped
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{kind} {value}" for kind, value in self.ops)
        key = "s0" if self.task_type == "low" else "s1"
        return texts.t(key, language, n=self.n, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kind=kind, value=value, low=low, popped=popped)
            for index, ((kind, value), (low, popped)) in enumerate(zip(self.ops, self.trace), 1)
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
