"""TwoPointerMergeTask — слияние двух неубывающих списков.

При равенстве берётся левый список. Длина результата растёт с уровнем.
Сколько элементов взято справа, пока левый список ещё не кончился, нельзя узнать по одной длине.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _rising(length: int, step: int) -> List[int]:
    value = random.randint(0, step)
    items = []
    for _ in range(length):
        value += random.randint(0, step)
        items.append(value)
    return items


class TwoPointerMergeTask(BaseMathTask):
    TASK_TYPE = "two_pointer_merge"
    TASK_TYPES = ["kth", "wins"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"a": 1, "b": 1, "s": 3}, 2: {"a": 2, "b": 1, "s": 3},
        3: {"a": 2, "b": 2, "s": 4}, 4: {"a": 3, "b": 2, "s": 4},
        5: {"a": 3, "b": 3, "s": 4}, 6: {"a": 4, "b": 3, "s": 5},
        7: {"a": 4, "b": 4, "s": 5}, 8: {"a": 5, "b": 4, "s": 5},
        9: {"a": 6, "b": 5, "s": 6}, 10: {"a": 6, "b": 6, "s": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        step = int(p["s"])
        self.left = _rising(max(1, int(p["a"])), step)
        self.right = _rising(max(1, int(p["b"])), step)
        self.merged: List[int] = []
        self.sources: List[str] = []
        self.wins = 0
        i = j = 0
        while i < len(self.left) or j < len(self.right):
            take_right = i == len(self.left) or (j < len(self.right) and self.right[j] < self.left[i])
            if take_right:
                self.merged.append(self.right[j])
                self.sources.append("R")
                if i < len(self.left):
                    self.wins += 1
                j += 1
            else:
                self.merged.append(self.left[i])
                self.sources.append("L")
                i += 1
        self.n = len(self.merged)
        self.k = random.randint(1, self.n)
        self.kth = self.merged[self.k - 1]
        self.answer = self.kth if self.task_type == "kth" else self.wins
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        left = ", ".join(str(item) for item in self.left)
        right = ", ".join(str(item) for item in self.right)
        key = "s0" if self.task_type == "kth" else "s1"
        return texts.t(key, language, left=left, right=right, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, value=value, source=source)
            for i, (value, source) in enumerate(zip(self.merged, self.sources), 1)
        ]
        steps.append(texts.t("s3", self.language, k=self.k, kth=self.kth, wins=self.wins))
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
