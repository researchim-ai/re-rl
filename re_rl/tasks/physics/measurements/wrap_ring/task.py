"""WrapRingTask — кольцевая сумма двух соседей.

Каждая ячейка становится суммой левого и правого соседей по кольцу.
Свёртку считает SciPy, накопленную сумму — SymPy. Длина ряда растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
import sympy as sp
from scipy.ndimage import convolve1d

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ring_sum(values: Sequence[int]) -> List[Tuple[int, int]]:
    row = np.asarray(list(values), dtype=np.int64)
    wrapped = convolve1d(row, np.array([1, 0, 1], dtype=np.int64), mode="wrap")
    total = sp.Integer(0)
    trace = []
    width = len(values)
    for index, value in enumerate(wrapped):
        direct = values[(index - 1) % width] + values[(index + 1) % width]
        if int(value) != direct:
            raise RuntimeError("ring mismatch")
        total += sp.Integer(int(value))
        trace.append((int(value), int(total)))
    return trace


class WrapRingTask(BaseMathTask):
    TASK_TYPE = "wrap_ring"
    TASK_TYPES = ["last", "total"]

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
        self.values = [random.randint(0, 6) for _ in range(self.n)]
        self.trace = ring_sum(self.values)
        self.last = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.last if self.task_type == "last" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, n=self.n, values=self._row(self.values))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, total=total)
            for index, (value, total) in enumerate(self.trace, 1)
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
