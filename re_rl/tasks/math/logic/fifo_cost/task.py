"""FifoCostTask — себестоимость продаж по очереди партий.

Покупка кладёт партию в конец. Продажа забирает товар из самых старых партий.
Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Event = Tuple[str, int, int]


def fifo_account(events: Sequence[Event]):
    lots: List[List[int]] = []
    cogs = 0
    trace = []
    for kind, qty, cost in events:
        if kind == "buy":
            lots.append([qty, cost])
        else:
            left = qty
            while left:
                take = min(lots[0][0], left)
                cogs += take * lots[0][1]
                lots[0][0] -= take
                left -= take
                if lots[0][0] == 0:
                    lots.pop(0)
        value = sum(count * price for count, price in lots)
        trace.append((cogs, value))
    value = sum(count * price for count, price in lots)
    return cogs, value, trace


class FifoCostTask(BaseMathTask):
    TASK_TYPE = "fifo_cost"
    TASK_TYPES = ["cogs", "value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "q": 3, "c": 4}, 2: {"n": 3, "q": 4, "c": 5},
        3: {"n": 4, "q": 4, "c": 5}, 4: {"n": 4, "q": 5, "c": 6},
        5: {"n": 5, "q": 5, "c": 6}, 6: {"n": 6, "q": 5, "c": 6},
        7: {"n": 7, "q": 6, "c": 7}, 8: {"n": 8, "q": 6, "c": 7},
        9: {"n": 10, "q": 6, "c": 8}, 10: {"n": 12, "q": 6, "c": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        qty_limit = max(1, int(p["q"]))
        cost_limit = max(1, int(p["c"]))
        self.events: List[Event] = []
        stock = 0
        sales = 0
        for index in range(self.n):
            force_sale = stock > 0 and index == self.n - 1 and sales == 0
            if stock == 0 or (not force_sale and random.random() < 0.55):
                qty = random.randint(1, qty_limit)
                cost = random.randint(1, cost_limit)
                self.events.append(("buy", qty, cost))
                stock += qty
            else:
                qty = random.randint(1, stock)
                self.events.append(("sell", qty, 0))
                stock -= qty
                sales += 1
        self.cogs, self.value, self.trace = fifo_account(self.events)
        self.answer = self.cogs if self.task_type == "cogs" else self.value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _event(self, language, event: Event) -> str:
        kind, qty, cost = event
        key = "s4" if kind == "buy" else "s5"
        return texts.t(key, language, qty=qty, cost=cost)

    def _descr(self, language):
        listing = "; ".join(self._event(language, event) for event in self.events)
        key = "s0" if self.task_type == "cogs" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, (event, (cogs, value)) in enumerate(zip(self.events, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, event=self._event(self.language, event),
                cogs=cogs, value=value,
            ))
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
