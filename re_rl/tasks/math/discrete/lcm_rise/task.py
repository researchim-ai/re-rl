"""LcmRiseTask — накопление наименьшего общего кратного.

Старт равен 1. На каждом числе значение заменяется на НОК с ним.
Считается итог и число строгих ростов. Длина списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lcm_trace(numbers: Sequence[int]) -> List[Tuple[int, int]]:
    current = 1
    rises = 0
    trace = []
    for value in numbers:
        nxt = current // math.gcd(current, value) * value
        if nxt > current:
            rises += 1
        current = nxt
        trace.append((current, rises))
    return trace


class LcmRiseTask(BaseMathTask):
    TASK_TYPE = "lcm_rise"
    TASK_TYPES = ["value", "rises"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 6}, 2: {"n": 2, "m": 8}, 3: {"n": 3, "m": 8},
        4: {"n": 4, "m": 9}, 5: {"n": 5, "m": 10}, 6: {"n": 6, "m": 10},
        7: {"n": 7, "m": 12}, 8: {"n": 8, "m": 12}, 9: {"n": 10, "m": 12},
        10: {"n": 12, "m": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(2, int(p["m"]))
        self.numbers = [random.randint(1, limit) for _ in range(self.n)]
        self.trace = lcm_trace(self.numbers)
        self.value, self.rises = self.trace[-1]
        self.answer = self.value if self.task_type == "value" else self.rises
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.numbers)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, current=current, rises=rises)
            for index, (value, (current, rises)) in enumerate(zip(self.numbers, self.trace), 1)
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
