"""ModAccumTask — сложение, вычитание и умножение по модулю 10.

После каждой операции берётся неотрицательный остаток от деления на 10.
Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def mod_ops(start: int, ops: Sequence[Op], modulo: int = 10) -> List[Tuple[int, int]]:
    value = start % modulo
    zeros = 0
    trace = []
    for code, arg in ops:
        if code == 0:
            value += arg
        elif code == 1:
            value -= arg
        else:
            value *= arg
        value %= modulo
        if value == 0:
            zeros += 1
        trace.append((value, zeros))
    return trace


class ModAccumTask(BaseMathTask):
    TASK_TYPE = "mod_accum"
    TASK_TYPES = ["value", "zeros"]
    MODULO = 10

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
        self.start = random.randint(0, self.MODULO - 1)
        self.ops = [(random.randint(0, 2), random.randint(0, 6)) for _ in range(self.n)]
        self.trace = mod_ops(self.start, self.ops, self.MODULO)
        self.value = self.trace[-1][0]
        self.zeros = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.zeros
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{code} {arg}" for code, arg in self.ops)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, mod=self.MODULO, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, arg=arg, value=value, zeros=zeros)
            for index, ((code, arg), (value, zeros)) in enumerate(zip(self.ops, self.trace), 1)
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
