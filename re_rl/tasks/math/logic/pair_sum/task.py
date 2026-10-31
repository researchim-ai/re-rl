"""PairSumTask — число неупорядоченных пар с заданной суммой.

Считаются пары индексов i < j, для которых a[i] + a[j] = target.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        data = " ".join(map(str, self.values))
        return ((texts.t('s0', language, data=data, target=self.target)))

    def solve(self):
        from re_rl.tasks.math.algorithm_traces.solvers import solve_detailed
        solve_detailed(self)

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
