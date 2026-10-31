"""RodCuttingTask — разрезание стержня с неограниченным числом разрезов.

prices[i] — цена куска длины i. Нужна максимальная выручка за стержень длины n.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rod_profit(prices: List[int]) -> int:
    """prices[i] — цена длины i, prices[0] не используется. Длина стержня = len-1."""
    n = len(prices) - 1
    dp = [0] * (n + 1)
    for length in range(1, n + 1):
        best = 0
        for cut in range(1, length + 1):
            best = max(best, prices[cut] + dp[length - cut])
        dp[length] = best
    return dp[n]


class RodCuttingTask(BaseMathTask):
    TASK_TYPE = "rod_cutting"
    TASK_TYPES = ["profit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "price": 8}, 2: {"n": 4, "price": 9}, 3: {"n": 4, "price": 10},
        4: {"n": 5, "price": 12}, 5: {"n": 5, "price": 12}, 6: {"n": 6, "price": 14},
        7: {"n": 7, "price": 15}, 8: {"n": 8, "price": 16}, 9: {"n": 8, "price": 18},
        10: {"n": 9, "price": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.price_max = int(p["price"])
        self.task_type = "profit"
        self.augment = augment
        self.prices = [0] + [random.randint(1, self.price_max) for _ in range(self.n)]
        self.answer = rod_profit(self.prices)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{i}: {self.prices[i]}" for i in range(1, self.n + 1))
        return ((texts.t('s0', language, n=self.n, shown=shown)))

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
