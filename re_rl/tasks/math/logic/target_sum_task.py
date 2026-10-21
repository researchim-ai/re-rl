"""TargetSumTask — сколькими способами знаки дают цель.

Каждому числу ставится плюс или минус. Порядок чисел фиксирован.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def target_ways(nums: List[int], target: int) -> int:
    ways = 0
    for mask in range(1 << len(nums)):
        total = 0
        for i, num in enumerate(nums):
            total += num if mask & (1 << i) else -num
        if total == target:
            ways += 1
    return ways


class TargetSumTask(BaseMathTask):
    TASK_TYPE = "target_sum"
    TASK_TYPES = ["ways"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 3}, 2: {"n": 4, "mag": 4}, 3: {"n": 4, "mag": 5},
        4: {"n": 5, "mag": 5}, 5: {"n": 5, "mag": 6}, 6: {"n": 6, "mag": 6},
        7: {"n": 7, "mag": 7}, 8: {"n": 8, "mag": 7}, 9: {"n": 9, "mag": 8},
        10: {"n": 10, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "ways"
        self.augment = augment
        self.nums = [random.randint(1, self.mag) for _ in range(self.n)]
        signed = sum(num if random.random() < 0.5 else -num for num in self.nums)
        self.target = signed
        self.answer = target_ways(self.nums, self.target)
        if self.answer < 1:
            raise RuntimeError("цель должна достигаться хотя бы одним набором знаков")
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.nums))
        return ((f"Числа: {data}. Каждому можно поставить плюс или минус. "
                 f"Сколько расстановок дают сумму {self.target}?") if ru else
                (f"Numbers: {data}. Each number may receive a plus or a minus. "
                 f"How many assignments sum to {self.target}?"))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Сумму {self.target} дают {self.answer} расстановок.") if ru else
                (f"{self.answer} assignments sum to {self.target}."))
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
