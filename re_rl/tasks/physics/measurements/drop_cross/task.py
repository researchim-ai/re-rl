"""DropCrossTask — капли разного размера и порог в колбе.

Сумма копится по порядку. Порог пересекается ровно на одной капле.
Число капель растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def running_sums(sizes: Sequence[int]) -> List[int]:
    total = 0
    sums = []
    for size in sizes:
        total += size
        sums.append(total)
    return sums


def first_cross(sums: Sequence[int], threshold: int) -> int:
    for index, total in enumerate(sums, 1):
        if total >= threshold:
            return index
    raise RuntimeError("cross")


class DropCrossTask(BaseMathTask):
    TASK_TYPE = "drop_cross"
    TASK_TYPES = ["cross", "excess"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 5}, 3: {"n": 4, "m": 5},
        4: {"n": 4, "m": 6}, 5: {"n": 5, "m": 6}, 6: {"n": 6, "m": 6},
        7: {"n": 7, "m": 7}, 8: {"n": 8, "m": 7}, 9: {"n": 10, "m": 8},
        10: {"n": 12, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.sizes = [random.randint(1, limit) for _ in range(self.n)]
        self.sums = running_sums(self.sizes)
        slot = random.randint(1, self.n)
        before = self.sums[slot - 2] if slot > 1 else 0
        self.threshold = before + random.randint(1, self.sizes[slot - 1])
        self.cross = first_cross(self.sums, self.threshold)
        self.excess = self.sums[-1] - self.threshold
        self.answer = self.cross if self.task_type == "cross" else self.excess
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(size) for size in self.sizes)
        key = "s0" if self.task_type == "cross" else "s1"
        return texts.t(key, language, n=self.n, threshold=self.threshold, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, size=size, total=total)
            for index, (size, total) in enumerate(zip(self.sizes, self.sums), 1)
        ]
        steps.append(texts.t("s3", self.language, cross=self.cross, excess=self.excess))
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
