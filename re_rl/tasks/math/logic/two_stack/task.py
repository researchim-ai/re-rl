"""TwoStackTask — очередь из двух стеков.

Новые числа кладутся в левый стек. Снятие берёт правый стек, а если он пуст, переливает в него весь левый и только потом снимает верх.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def queue_trace(ops: Sequence[Op]) -> List[Tuple[int, int, int]]:
    inbox: List[int] = []
    outbox: List[int] = []
    pours = 0
    got = 0
    trace = []
    for kind, value in ops:
        out = 0
        if kind == 0:
            inbox.append(value)
        else:
            if not outbox and inbox:
                pours += 1
                while inbox:
                    outbox.append(inbox.pop())
            if outbox:
                out = outbox.pop()
                got += out
        trace.append((out, got, pours))
    return trace


class TwoStackTask(BaseMathTask):
    TASK_TYPE = "two_stack"
    TASK_TYPES = ["got", "pours"]

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
            value = random.randint(1, 6) if kind == 0 else 0
            self.ops.append((kind, value))
        self.trace = queue_trace(self.ops)
        self.got = self.trace[-1][1]
        self.pours = self.trace[-1][2]
        self.answer = self.got if self.task_type == "got" else self.pours
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{kind} {value}" for kind, value in self.ops)
        key = "s0" if self.task_type == "got" else "s1"
        return texts.t(key, language, n=self.n, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kind=kind, value=value, out=out, got=got, pours=pours)
            for index, ((kind, value), (out, got, pours)) in enumerate(zip(self.ops, self.trace), 1)
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
