"""PartitionCountTask — разбиения целого числа.

Обычные разбиения и разбиения на различные части считаются динамикой.
Число, которое раскладываем, растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def partition_ways(limit: int) -> List[int]:
    ways = [0] * (limit + 1)
    ways[0] = 1
    trace = []
    for part in range(1, limit + 1):
        for total in range(part, limit + 1):
            ways[total] += ways[total - part]
        trace.append(ways[limit])
    return trace


def distinct_ways(limit: int) -> List[int]:
    ways = [0] * (limit + 1)
    ways[0] = 1
    trace = []
    for part in range(1, limit + 1):
        for total in range(limit, part - 1, -1):
            ways[total] += ways[total - part]
        trace.append(ways[limit])
    return trace


class PartitionCountTask(BaseMathTask):
    TASK_TYPE = "partition_count"
    TASK_TYPES = ["count", "distinct"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 7},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 13},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.count_trace = partition_ways(self.n)
        self.distinct_trace = distinct_ways(self.n)
        self.count = self.count_trace[-1]
        self.distinct = self.distinct_trace[-1]
        if self.task_type == "count":
            self.trace = self.count_trace
            self.answer = self.count
        else:
            self.trace = self.distinct_trace
            self.answer = self.distinct
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        rule = texts.t("s4" if self.task_type == "count" else "s5", self.language)
        steps = [
            texts.t("s2", self.language, part=part, n=self.n, ways=ways, rule=rule)
            for part, ways in enumerate(self.trace, 1)
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
