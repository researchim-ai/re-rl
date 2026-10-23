"""BeadCountTask — ожерелья из двух цветов с точностью до поворота.

Число раскрасок — среднее число неподвижных раскрасок по всем поворотам.
Число бусин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def bead_trace(count: int) -> List[Tuple[int, int, int]]:
    total = 0
    trace = []
    for turn in range(count):
        gap = math.gcd(turn, count)
        fixed = 2 ** gap
        total += fixed
        trace.append((gap, fixed, total))
    return trace


class BeadCountTask(BaseMathTask):
    TASK_TYPE = "bead_count"
    TASK_TYPES = ["count", "fixed"]

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
        self.trace = bead_trace(self.n)
        self.k = random.randint(1, self.n)
        self.fixed = self.trace[self.k - 1][1]
        self.count = self.trace[-1][2] // self.n
        self.answer = self.count if self.task_type == "count" else self.fixed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gap=gap, fixed=fixed, total=total)
            for index, (gap, fixed, total) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, total=self.trace[-1][2], n=self.n, count=self.count))
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
