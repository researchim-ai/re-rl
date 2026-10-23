"""StreamMedianTask — медиана растущего списка.

После каждого числа список сортируется. При чётной длине берётся левый из двух средних.
Число добавлений нечётно и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def median_trace(values: Sequence[int]) -> Tuple[List[int], int]:
    ordered = []
    medians = []
    for value in values:
        index = 0
        while index < len(ordered) and ordered[index] <= value:
            index += 1
        ordered.insert(index, value)
        medians.append(ordered[(len(ordered) - 1) // 2])
    flips = sum(medians[i] != medians[i - 1] for i in range(1, len(medians)))
    return medians, flips


class StreamMedianTask(BaseMathTask):
    TASK_TYPE = "stream_median"
    TASK_TYPES = ["median", "flips"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 5}, 3: {"n": 5, "m": 6},
        4: {"n": 5, "m": 8}, 5: {"n": 7, "m": 8}, 6: {"n": 7, "m": 10},
        7: {"n": 9, "m": 12}, 8: {"n": 11, "m": 12}, 9: {"n": 13, "m": 15},
        10: {"n": 15, "m": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        if self.n % 2 == 0:
            self.n += 1
        limit = max(1, int(p["m"]))
        self.values = [random.randint(0, limit) for _ in range(self.n)]
        self.medians, self.flips = median_trace(self.values)
        self.median = self.medians[-1]
        self.answer = self.median if self.task_type == "median" else self.flips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "median" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, median=median)
            for index, (value, median) in enumerate(zip(self.values, self.medians), 1)
        ]
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
