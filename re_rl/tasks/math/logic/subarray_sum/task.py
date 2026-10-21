"""SubarraySumTask — сколько непрерывных подмассивов дают заданную сумму.

Пустой подмассив не считается. Цель выбирается как сумма хотя бы одного отрезка.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def subarray_count(nums: List[int], target: int) -> int:
    count = 0
    prefix = 0
    seen = {0: 1}
    for value in nums:
        prefix += value
        count += seen.get(prefix - target, 0)
        seen[prefix] = seen.get(prefix, 0) + 1
    return count


class SubarraySumTask(BaseMathTask):
    TASK_TYPE = "subarray_sum"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "mag": 3}, 2: {"n": 5, "mag": 4}, 3: {"n": 5, "mag": 4},
        4: {"n": 6, "mag": 5}, 5: {"n": 6, "mag": 6}, 6: {"n": 7, "mag": 6},
        7: {"n": 8, "mag": 7}, 8: {"n": 9, "mag": 8}, 9: {"n": 10, "mag": 8},
        10: {"n": 12, "mag": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "count"
        self.augment = augment
        low = 0 if difficulty < 4 else -self.mag
        self.nums = [random.randint(low, self.mag) for _ in range(self.n)]
        left = random.randrange(self.n)
        right = random.randrange(left, self.n)
        self.target = sum(self.nums[left:right + 1])
        self.answer = subarray_count(self.nums, self.target)
        if self.answer < 1:
            raise RuntimeError(texts.t('s2', language))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.nums))
        return ((texts.t('s0', language, data=data, target=self.target)))

    def solve(self):
        step = ((texts.t('s1', self.language, target=self.target, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
