"""StirlingSecondTask — числа Стирлинга второго рода и числа Белла.

S(n, k) — число разбиений n-элементного множества на k непустых частей.
S(n, k) = k * S(n-1, k) + S(n-1, k-1). Число Белла B(n) = sum_k S(n, k).
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stirling_row(n: int) -> list:
    """S(n, 0)..S(n, n)."""
    row = [0] * (n + 1)
    if n == 0:
        row[0] = 1
        return row
    prev = [1]  # S(0, 0) = 1
    for i in range(1, n + 1):
        cur = [0] * (i + 1)
        for k in range(1, i + 1):
            left = prev[k] if k < len(prev) else 0
            right = prev[k - 1]
            cur[k] = k * left + right
        prev = cur
    return prev


class StirlingSecondTask(BaseMathTask):
    TASK_TYPE = "stirling_second"
    TASK_TYPES = ["stirling", "bell"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.row = stirling_row(self.n)
        if self.task_type == "stirling":
            self.k = random.randint(1, self.n)
            self.answer = self.row[self.k]
        else:
            self.answer = sum(self.row)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "stirling":
            return ((f"S(n, k) — число разбиений n элементов на k непустых подмножеств, "
                     f"S(n, k) = k*S(n-1, k) + S(n-1, k-1), S(0, 0) = 1. "
                     f"Найдите S({self.n}, {self.k}).") if ru else
                    (f"S(n, k) is the number of ways to partition n elements into k nonempty subsets, "
                     f"S(n, k) = k*S(n-1, k) + S(n-1, k-1), S(0, 0) = 1. "
                     f"Find S({self.n}, {self.k})."))
        return ((f"Число Белла B(n) — число всех разбиений n-элементного множества, "
                 f"B(n) = сумма S(n, k) по k. Найдите B({self.n}).") if ru else
                (f"The Bell number B(n) counts all partitions of an n-element set, "
                 f"B(n) = sum of S(n, k). Find B({self.n})."))

    def solve(self):
        ru = self.language == "ru"
        shown = ", ".join(f"S({self.n}, {k})={self.row[k]}" for k in range(1, self.n + 1))
        self.solution_steps = [
            shown + ".",
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
