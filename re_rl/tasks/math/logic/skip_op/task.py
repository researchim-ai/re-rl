"""SkipOpTask — значение после цепочки и то же значение без одного шага.

Шаг либо прибавляет число, либо умножает на него. Второй проход выкидывает шаг k.
Оба прохода линейные, множители маленькие.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[str, int]


def apply_ops(start: int, ops: Sequence[Op]) -> List[int]:
    value = start
    trace = []
    for kind, amount in ops:
        value = value + amount if kind == "add" else value * amount
        trace.append(value)
    return trace


class SkipOpTask(BaseMathTask):
    TASK_TYPE = "skip_op"
    TASK_TYPES = ["final", "without"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(1, 4)
        self.ops = []
        for _ in range(self.n):
            if random.randint(0, 1) == 0:
                self.ops.append(("add", random.randint(1, 5)))
            else:
                self.ops.append(("mul", random.randint(2, 3)))
        self.full = apply_ops(self.start, self.ops)
        self.k = random.randint(1, self.n)
        reduced = self.ops[:self.k - 1] + self.ops[self.k:]
        self.reduced = apply_ops(self.start, reduced)
        self.final = self.full[-1]
        self.without = self.reduced[-1] if self.reduced else self.start
        self.answer = self.final if self.task_type == "final" else self.without
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _op(self, language, op: Op) -> str:
        kind, amount = op
        key = "s4" if kind == "add" else "s5"
        return texts.t(key, language, value=amount)

    def _descr(self, language):
        listing = "; ".join(self._op(language, op) for op in self.ops)
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=listing, k=self.k)

    def solve(self):
        if self.task_type == "final":
            steps = [
                texts.t("s2", self.language, i=index, op=self._op(self.language, op), value=value)
                for index, (op, value) in enumerate(zip(self.ops, self.full), 1)
            ]
        else:
            steps = []
            cursor = 0
            for index, op in enumerate(self.ops, 1):
                if index == self.k:
                    steps.append(texts.t("s6", self.language, i=index))
                else:
                    steps.append(texts.t(
                        "s2", self.language, i=index, op=self._op(self.language, op),
                        value=self.reduced[cursor],
                    ))
                    cursor += 1
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
