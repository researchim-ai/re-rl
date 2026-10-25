"""LcgStepTask — шаг линейного конгруэнтного генератора.

Новое значение равно остатку от деления произведения со сдвигом на 10.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def lcg_trace(start: int, steps: Sequence[Step], modulo: int = 10) -> List[Tuple[int, int]]:
    value = start % modulo
    zeros = 0
    trace = []
    for mul, add in steps:
        value = (value * mul + add) % modulo
        if value == 0:
            zeros += 1
        trace.append((value, zeros))
    return trace


class LcgStepTask(BaseMathTask):
    TASK_TYPE = "lcg_step"
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
        self.steps = [(random.randint(1, 4), random.randint(0, 5)) for _ in range(self.n)]
        self.trace = lcg_trace(self.start, self.steps, self.MODULO)
        self.value = self.trace[-1][0]
        self.zeros = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.zeros
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{mul} {add}" for mul, add in self.steps)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, mod=self.MODULO, steps=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, mul=mul, add=add, value=value, zeros=zeros)
            for index, ((mul, add), (value, zeros)) in enumerate(zip(self.steps, self.trace), 1)
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
