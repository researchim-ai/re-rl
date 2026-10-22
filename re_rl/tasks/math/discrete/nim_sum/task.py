"""NimSumTask — ним-сумма нескольких куч.

Побеждает тот, кто забирает последний предмет. Позиция выигрышна, когда XOR куч не ноль.
Число куч растёт с уровнем, сумма считается слева направо.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def running_xor(heaps: List[int]) -> List[int]:
    total = 0
    trace = []
    for size in heaps:
        total ^= size
        trace.append(total)
    return trace


class NimSumTask(BaseMathTask):
    TASK_TYPE = "nim_sum"
    TASK_TYPES = ["total", "winning"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "s": 4}, 2: {"n": 3, "s": 5}, 3: {"n": 4, "s": 6},
        4: {"n": 4, "s": 7}, 5: {"n": 5, "s": 8}, 6: {"n": 6, "s": 8},
        7: {"n": 7, "s": 10}, 8: {"n": 8, "s": 10}, 9: {"n": 9, "s": 12},
        10: {"n": 10, "s": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["s"])
        self.heaps = [random.randint(0, limit) for _ in range(self.n)]
        self.trace = running_xor(self.heaps)
        self.nim = self.trace[-1]
        self.winning = 1 if self.nim else 0
        self.answer = self.nim if self.task_type == "total" else self.winning
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.heaps)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, size=size, total=total)
            for i, (size, total) in enumerate(zip(self.heaps, self.trace), 1)
        ]
        steps.append(texts.t("s3", self.language, nim=self.nim, winning=self.winning))
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
