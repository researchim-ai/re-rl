"""DutchFlagTask — трёхцветное разбиение за один проход.

Ноль уезжает влево, двойка вправо, единица остаётся. Каждый шаг сдвигает одну границу.
Длина массива растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def dutch_trace(colors: Sequence[int]) -> Tuple[int, int, List[int]]:
    items = list(colors)
    low = 0
    mid = 0
    high = len(items) - 1
    swaps = 0
    moved = 0
    while mid <= high:
        color = items[mid]
        if color == 0:
            if low != mid:
                items[low], items[mid] = items[mid], items[low]
                swaps += 1
            low += 1
            mid += 1
        elif color == 1:
            mid += 1
        else:
            if mid != high:
                items[mid], items[high] = items[high], items[mid]
                swaps += 1
                moved += 1
            high -= 1
    return swaps, moved, items


class DutchFlagTask(BaseMathTask):
    TASK_TYPE = "dutch_flag"
    TASK_TYPES = ["swaps", "twos"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.colors = [random.randint(0, 2) for _ in range(self.n)]
        self.swaps, self.twos, self.final = dutch_trace(self.colors)
        self.answer = self.swaps if self.task_type == "swaps" else self.twos
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(color) for color in self.colors)
        key = "s0" if self.task_type == "swaps" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, color=color)
            for index, color in enumerate(self.colors, 1)
        ]
        steps.append(texts.t("s3", self.language, swaps=self.swaps, twos=self.twos))
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
