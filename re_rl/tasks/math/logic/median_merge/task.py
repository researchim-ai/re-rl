"""MedianMergeTask — слияние двух упорядоченных списков.

На каждом шаге берётся меньший из оставшихся голов. При равенстве берётся левый список.
Длина каждого списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def merge_trace(left: Sequence[int], right: Sequence[int]) -> Tuple[List[int], List[Tuple[int, int, int]]]:
    i = 0
    j = 0
    merged = []
    trace = []
    while i < len(left) or j < len(right):
        take_left = j == len(right) or (i < len(left) and left[i] <= right[j])
        if take_left:
            merged.append(left[i])
            i += 1
            side = 0
        else:
            merged.append(right[j])
            j += 1
            side = 1
        trace.append((merged[-1], side, i))
    return merged, trace


class MedianMergeTask(BaseMathTask):
    TASK_TYPE = "median_merge"
    TASK_TYPES = ["median", "lefts"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.left = sorted(random.randint(0, 20) for _ in range(self.n))
        self.right = sorted(random.randint(0, 20) for _ in range(self.n))
        self.merged, self.trace = merge_trace(self.left, self.right)
        self.median = self.merged[self.n - 1]
        self.lefts = self.trace[self.n - 1][2]
        self.answer = self.median if self.task_type == "median" else self.lefts
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        left = ", ".join(str(item) for item in self.left)
        right = ", ".join(str(item) for item in self.right)
        key = "s0" if self.task_type == "median" else "s1"
        return texts.t(key, language, n=self.n, left=left, right=right)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, side=side, taken=taken)
            for index, (value, side, taken) in enumerate(self.trace, 1)
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
