"""HistogramTask — наибольший прямоугольник под столбцами гистограммы.

Ширина столбца равна 1. Прямоугольник обязан целиком помещаться под столбцами.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def largest_rectangle(heights: List[int]) -> int:
    stack = [-1]
    best = 0
    extended = list(heights) + [0]
    for i, height in enumerate(extended):
        while stack[-1] != -1 and extended[stack[-1]] > height:
            bar = extended[stack.pop()]
            width = i - stack[-1] - 1
            area = bar * width
            if area > best:
                best = area
        stack.append(i)
    return best


class HistogramTask(BaseMathTask):
    TASK_TYPE = "histogram_area"
    TASK_TYPES = ["area"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "h": 4}, 2: {"n": 4, "h": 5}, 3: {"n": 5, "h": 5},
        4: {"n": 5, "h": 6}, 5: {"n": 6, "h": 7}, 6: {"n": 7, "h": 8},
        7: {"n": 8, "h": 9}, 8: {"n": 10, "h": 10}, 9: {"n": 12, "h": 12},
        10: {"n": 14, "h": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.h = int(p["h"])
        self.task_type = "area"
        self.augment = augment
        self.heights = [random.randint(0, self.h) for _ in range(self.n)]
        self.answer = largest_rectangle(self.heights)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.heights))
        return ((f"Высоты столбцов гистограммы слева направо: {data}. Ширина каждого столбца равна 1. "
                 f"Найдите наибольшую площадь прямоугольника, который целиком лежит под столбцами.")
                if ru else
                (f"Histogram bar heights from left to right: {data}. Each bar has width 1. "
                 f"Find the largest area of a rectangle that lies entirely under the bars."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Наибольшая площадь равна {self.answer}.") if ru else
                (f"The largest area is {self.answer}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
