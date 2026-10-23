"""HookLengthTask — число таблиц Юнга по формуле крюков.

Крюк клетки — клетки справа, клетки ниже и сама клетка. Факториал числа клеток делится на произведение крюков.
Число клеток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hook_trace(parts: List[int]) -> Tuple[List[Tuple[int, int, int, int]], int]:
    cells = []
    product = 1
    for row, width in enumerate(parts, 1):
        for column in range(1, width + 1):
            arm = width - column
            leg = sum(1 for below in parts[row:] if below >= column)
            hook = arm + leg + 1
            product *= hook
            cells.append((row, column, hook, product))
    boxes = sum(parts)
    fact = math.factorial(boxes)
    assert fact % product == 0
    return cells, fact // product


def random_shape(boxes: int) -> List[int]:
    parts = []
    left = boxes
    cap = boxes
    while left:
        part = random.randint(1, min(cap, left))
        parts.append(part)
        left -= part
        cap = part
    return parts


class HookLengthTask(BaseMathTask):
    TASK_TYPE = "hook_length"
    TASK_TYPES = ["dim", "hook"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.parts = random_shape(self.n)
        self.cells, self.dim = hook_trace(self.parts)
        self.fact = math.factorial(self.n)
        self.k = random.randint(1, self.n)
        self.hook = self.cells[self.k - 1][2]
        self.answer = self.dim if self.task_type == "dim" else self.hook
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "dim" else "s1"
        shape = ", ".join(str(part) for part in self.parts)
        return texts.t(key, language, n=self.n, shape=shape, k=self.k, fact=self.fact)

    def solve(self):
        steps = [
            texts.t("s2", self.language, row=row, column=column, hook=hook, product=product)
            for row, column, hook, product in self.cells
        ]
        steps.append(texts.t("s3", self.language, fact=self.fact, product=self.cells[-1][3], dim=self.dim))
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
