"""StockSpanTask — размах цены влево до строго большей.

Размах дня равен 1 плюс число подряд идущих предыдущих цен, которые не больше сегодняшней.
Число дней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stock_spans(prices: Sequence[int]) -> List[int]:
    spans = []
    for index, price in enumerate(prices):
        span = 1
        cursor = index - 1
        while cursor >= 0 and prices[cursor] <= price:
            span += 1
            cursor -= 1
        spans.append(span)
    return spans


class StockSpanTask(BaseMathTask):
    TASK_TYPE = "stock_span"
    TASK_TYPES = ["total", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 6}, 2: {"n": 3, "m": 8}, 3: {"n": 4, "m": 8},
        4: {"n": 5, "m": 10}, 5: {"n": 6, "m": 10}, 6: {"n": 8, "m": 12},
        7: {"n": 10, "m": 12}, 8: {"n": 11, "m": 14}, 9: {"n": 12, "m": 14},
        10: {"n": 14, "m": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(2, int(p["m"]))
        self.prices = [random.randint(1, limit) for _ in range(self.n)]
        self.spans = stock_spans(self.prices)
        self.total = sum(self.spans)
        self.k = random.randint(1, self.n)
        self.at_k = self.spans[self.k - 1]
        self.answer = self.total if self.task_type == "total" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(price) for price in self.prices)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, price=price, span=span)
            for index, (price, span) in enumerate(zip(self.prices, self.spans), 1)
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
