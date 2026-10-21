"""MaxProductTask — наибольшее произведение непрерывного подмассива.

Подмассив непустой. Отрицательные числа и нули разрешены.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def max_product(nums: List[int]) -> int:
    best = cur_max = cur_min = nums[0]
    for value in nums[1:]:
        options = (value, cur_max * value, cur_min * value)
        cur_max = max(options)
        cur_min = min(options)
        if cur_max > best:
            best = cur_max
    return best


class MaxProductTask(BaseMathTask):
    TASK_TYPE = "max_product"
    TASK_TYPES = ["product"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 4}, 2: {"n": 4, "mag": 4}, 3: {"n": 4, "mag": 5},
        4: {"n": 5, "mag": 5}, 5: {"n": 5, "mag": 6}, 6: {"n": 6, "mag": 6},
        7: {"n": 7, "mag": 7}, 8: {"n": 8, "mag": 7}, 9: {"n": 9, "mag": 8},
        10: {"n": 10, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "product"
        self.augment = augment
        self.nums = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.answer = max_product(self.nums)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.nums))
        return ((f"Массив: {data}. Найдите наибольшее произведение непустого непрерывного подмассива.")
                if ru else
                (f"Array: {data}. Find the largest product of a nonempty contiguous subarray."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Наибольшее произведение равно {self.answer}.") if ru else
                (f"The largest product is {self.answer}."))
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
