"""BilliardCrossTask — клетки, которые пересекает луч под 45 градусов.

Луч идёт из угла 0,0 прямоугольника a на b. Число клеток равно a+b минус наибольший общий делитель.
Стороны растут с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def billiard_trace(width: int, height: int) -> Tuple[List[int], int]:
    x = 0
    y = 0
    squares = 0
    corners = 0
    trace = []
    while x < width or y < height:
        squares += 1
        trace.append(squares)
        if x == width:
            y += 1
        elif y == height:
            x += 1
        elif (x + 1) * height < (y + 1) * width:
            x += 1
        elif (x + 1) * height > (y + 1) * width:
            y += 1
        else:
            x += 1
            y += 1
            corners += 1
    assert squares == width + height - math.gcd(width, height)
    assert corners == math.gcd(width, height)
    return trace, corners


class BilliardCrossTask(BaseMathTask):
    TASK_TYPE = "billiard_cross"
    TASK_TYPES = ["squares", "corners"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 2, "b": 3}, 2: {"a": 2, "b": 3}, 3: {"a": 3, "b": 4},
        4: {"a": 3, "b": 5}, 5: {"a": 4, "b": 7}, 6: {"a": 5, "b": 7},
        7: {"a": 5, "b": 8}, 8: {"a": 6, "b": 7}, 9: {"a": 7, "b": 9},
        10: {"a": 8, "b": 11},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.width = int(p["a"])
        self.height = int(p["b"])
        self.trace, self.corners = billiard_trace(self.width, self.height)
        self.n = len(self.trace)
        self.squares = self.n
        self.answer = self.squares if self.task_type == "squares" else self.corners
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "squares" else "s1"
        return texts.t(key, language, width=self.width, height=self.height)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, squares=squares)
            for index, squares in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, corners=self.corners, squares=self.squares))
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
