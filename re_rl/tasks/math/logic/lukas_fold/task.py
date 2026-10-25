"""LukasFoldTask — свёртка степеней истинности по Лукасевичу.

Накопитель идёт слева направо. Конъюнкция, дизъюнкция и импликация считаются по целым формулам со шкалой 0..4.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lukas_apply(acc: int, op: int, other: int, bound: int) -> int:
    if op == 0:
        return max(0, acc + other - bound)
    if op == 1:
        return min(bound, acc + other)
    return min(bound, bound - acc + other)


def lukas_trace(start: int, ops: Sequence[Tuple[int, int]], bound: int) -> List[Tuple[int, int]]:
    acc = start
    zeros = 0
    trace = []
    for op, other in ops:
        acc = lukas_apply(acc, op, other, bound)
        if acc == 0:
            zeros += 1
        trace.append((acc, zeros))
    return trace


class LukasFoldTask(BaseMathTask):
    TASK_TYPE = "lukas_fold"
    TASK_TYPES = ["degree", "zeros"]
    BOUND = 4

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
        self.bound = self.BOUND
        self.start = random.randint(0, self.bound)
        self.ops = [
            (random.randint(0, 2), random.randint(0, self.bound))
            for _ in range(self.n)
        ]
        self.trace = lukas_trace(self.start, self.ops, self.bound)
        self.degree = self.trace[-1][0]
        self.zeros = self.trace[-1][1]
        self.answer = self.degree if self.task_type == "degree" else self.zeros
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{op} {other}" for op, other in self.ops)
        key = "s0" if self.task_type == "degree" else "s1"
        return texts.t(
            key, language, n=self.n, bound=self.bound, start=self.start, steps=shown,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=op, other=other, acc=acc, zeros=zeros)
            for index, ((op, other), (acc, zeros)) in enumerate(zip(self.ops, self.trace), 1)
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
