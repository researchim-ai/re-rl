"""ContainerWaterTask — максимум воды между двумя линиями.

Площадь пары i < j равна min(height[i], height[j]) * (j - i).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def max_water(heights: List[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        area = min(heights[left], heights[right]) * (right - left)
        if area > best:
            best = area
        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1
    return best


class ContainerWaterTask(BaseMathTask):
    TASK_TYPE = "container_water"
    TASK_TYPES = ["area"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "h": 6}, 2: {"n": 5, "h": 7}, 3: {"n": 5, "h": 8},
        4: {"n": 6, "h": 9}, 5: {"n": 7, "h": 10}, 6: {"n": 8, "h": 10},
        7: {"n": 9, "h": 12}, 8: {"n": 10, "h": 12}, 9: {"n": 12, "h": 14},
        10: {"n": 14, "h": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.h = int(p["h"])
        self.task_type = "area"
        self.augment = augment
        self.heights = [random.randint(1, self.h) for _ in range(self.n)]
        self.answer = max_water(self.heights)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.heights))
        return ((texts.t('s0', language, data=data)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
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
