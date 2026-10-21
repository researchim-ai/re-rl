"""StockProfitTask — одна покупка и одна продажа акции.

Прибыль = цена продажи минус цена покупки, продажа строго позже покупки.
Если выгоды нет, прибыль 0: можно не торговать.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def max_profit(prices: List[int]) -> int:
    best = 0
    low = prices[0]
    for price in prices[1:]:
        if price - low > best:
            best = price - low
        if price < low:
            low = price
    return best


class StockProfitTask(BaseMathTask):
    TASK_TYPE = "stock_profit"
    TASK_TYPES = ["profit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "mag": 8}, 2: {"n": 5, "mag": 10}, 3: {"n": 6, "mag": 12},
        4: {"n": 6, "mag": 15}, 5: {"n": 7, "mag": 15}, 6: {"n": 8, "mag": 20},
        7: {"n": 9, "mag": 20}, 8: {"n": 10, "mag": 25}, 9: {"n": 12, "mag": 30},
        10: {"n": 14, "mag": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "profit"
        self.augment = augment
        self.prices = [random.randint(1, self.mag) for _ in range(self.n)]
        self.answer = max_profit(self.prices)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.prices))
        return ((f"Цены акции по дням: {data}. Можно купить один раз и позже продать один раз. "
                 f"Если прибыли нет, ответ 0. Найдите максимальную прибыль.") if ru else
                (f"Stock prices by day: {data}. You may buy once and sell once later. "
                 f"If there is no profit, the answer is 0. Find the maximum profit."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Минимум слева и лучшая разница справа дают {self.answer}.") if ru else
             (f"The best difference after a left-side minimum is {self.answer}.")),
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
