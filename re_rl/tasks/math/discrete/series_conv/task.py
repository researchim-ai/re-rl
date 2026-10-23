"""SeriesConvTask — полная дискретная свёртка двух рядов.

Выход номер k складывает произведения членов, чьи индексы дают k.
Длина первого ряда растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def conv_full(left: Sequence[int], right: Sequence[int]) -> List[int]:
    output = []
    for index in range(len(left) + len(right) - 1):
        total = 0
        for left_index, value in enumerate(left):
            right_index = index - left_index
            if 0 <= right_index < len(right):
                total += value * right[right_index]
        output.append(total)
    return output


def conv_poly(left: Sequence[int], right: Sequence[int]) -> List[int]:
    symbol = sp.symbols("x")
    left_poly = sum(value * symbol ** index for index, value in enumerate(left))
    right_poly = sum(value * symbol ** index for index, value in enumerate(right))
    product = sp.expand(left_poly * right_poly)
    width = len(left) + len(right) - 1
    return [int(product.coeff(symbol, index)) for index in range(width)]


class SeriesConvTask(BaseMathTask):
    TASK_TYPE = "series_conv"
    TASK_TYPES = ["at", "total"]

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
        self.left = [random.randint(-2, 3) for _ in range(self.n)]
        self.right = [random.randint(-2, 3) for _ in range(3)]
        self.output = conv_full(self.left, self.right)
        assert self.output == conv_poly(self.left, self.right)
        self.k = random.randint(1, len(self.output))
        self.at = self.output[self.k - 1]
        self.total = sum(self.output)
        self.answer = self.at if self.task_type == "at" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        left = ", ".join(str(value) for value in self.left)
        right = ", ".join(str(value) for value in self.right)
        key = "s0" if self.task_type == "at" else "s1"
        return texts.t(key, language, n=self.n, left=left, right=right, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.output, 1)
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
