"""StockUnlimitedTask — максимум прибыли при любом числе сделок.

Одновременно можно держать не больше одной акции: продать нужно раньше следующей покупки.
Это сумма всех соседних повышений цены. Если роста нет, прибыль 0.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def unlimited_profit(prices: List[int]) -> int:
    return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))


class StockUnlimitedTask(BaseMathTask):
    TASK_TYPE = "stock_unlimited"
    TASK_TYPES = ["profit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 6}, 2: {"n": 4, "mag": 8}, 3: {"n": 4, "mag": 10},
        4: {"n": 5, "mag": 12}, 5: {"n": 6, "mag": 12}, 6: {"n": 7, "mag": 15},
        7: {"n": 8, "mag": 18}, 8: {"n": 9, "mag": 20}, 9: {"n": 10, "mag": 24},
        10: {"n": 12, "mag": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "profit"
        self.augment = augment
        self.prices = [random.randint(1, self.mag) for _ in range(self.n)]
        self.answer = unlimited_profit(self.prices)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.prices))
        return ((texts.t('s0', language, data=data)))

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
