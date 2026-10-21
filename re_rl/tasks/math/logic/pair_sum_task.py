"""PairSumTask — число неупорядоченных пар с заданной суммой.

Считаются пары индексов i < j, для которых a[i] + a[j] = target.
"""

import random
from collections import Counter
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def count_pairs(values: List[int], target: int) -> int:
    seen: Counter = Counter()
    total = 0
    for value in values:
        total += seen[target - value]
        seen[value] += 1
    return total


class PairSumTask(BaseMathTask):
    TASK_TYPE = "pair_sum"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "mag": 6}, 2: {"n": 6, "mag": 7}, 3: {"n": 7, "mag": 8},
        4: {"n": 8, "mag": 8}, 5: {"n": 9, "mag": 9}, 6: {"n": 10, "mag": 10},
        7: {"n": 12, "mag": 10}, 8: {"n": 14, "mag": 12}, 9: {"n": 16, "mag": 12},
        10: {"n": 18, "mag": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "count"
        self.augment = augment
        self.values = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        # Гарантируем хотя бы одну пару, подменив два элемента.
        if random.random() < 0.8:
            i, j = random.sample(range(self.n), 2)
            base = random.randint(-self.mag, self.mag)
            other = random.randint(-self.mag, self.mag)
            self.values[i] = base
            self.values[j] = other
            self.target = base + other
        else:
            self.target = random.randint(-self.mag, self.mag)
        self.answer = count_pairs(self.values, self.target)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.values))
        return ((f"Сколько пар индексов i < j в массиве {data} дают сумму {self.target}?") if ru else
                (f"How many index pairs i < j in the array {data} sum to {self.target}?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Перебор пар с накопленным счётчиком даёт {self.answer}.") if ru else
             (f"A counting pass over pairs gives {self.answer}.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
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
