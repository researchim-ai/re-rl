"""TrappingRainTask — сколько воды удерживает рельеф.

Между столбцами вода доходит до минимума из ближайших больших стенок слева и справа.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def trap(heights: List[int]) -> int:
    left, right = 0, len(heights) - 1
    left_max, right_max = heights[0], heights[-1]
    water = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, heights[left])
            water += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            water += right_max - heights[right]
    return water


class TrappingRainTask(BaseMathTask):
    TASK_TYPE = "trapping_rain"
    TASK_TYPES = ["water"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "h": 3}, 2: {"n": 5, "h": 4}, 3: {"n": 6, "h": 4},
        4: {"n": 6, "h": 5}, 5: {"n": 7, "h": 5}, 6: {"n": 8, "h": 6},
        7: {"n": 9, "h": 6}, 8: {"n": 10, "h": 7}, 9: {"n": 12, "h": 7},
        10: {"n": 14, "h": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.h = int(p["h"])
        self.task_type = "water"
        self.augment = augment
        self.heights = [random.randint(0, self.h) for _ in range(self.n)]
        self.answer = trap(self.heights)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.heights))
        return ((texts.t('s0', language, data=data)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
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
