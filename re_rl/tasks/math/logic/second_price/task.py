"""SecondPriceTask — аукцион второй цены.

Побеждает наибольшая ставка. При равенстве побеждает меньший номер.
Платёж — максимум ставок остальных участников.

Подтипы: номер победителя и его платёж.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def second_price(bids: List[int]) -> Tuple[int, int]:
    """Возвращает (номер победителя с 1, платёж)."""
    best = max(bids)
    winner = min(i for i, b in enumerate(bids) if b == best)
    payment = max(b for i, b in enumerate(bids) if i != winner)
    return winner + 1, payment


class SecondPriceTask(BaseMathTask):
    TASK_TYPE = "second_price"
    TASK_TYPES = ["winner", "payment"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "bid": 10}, 2: {"n": 3, "bid": 15}, 3: {"n": 4, "bid": 20},
        4: {"n": 4, "bid": 25}, 5: {"n": 5, "bid": 30}, 6: {"n": 5, "bid": 40},
        7: {"n": 6, "bid": 40}, 8: {"n": 6, "bid": 50}, 9: {"n": 7, "bid": 60},
        10: {"n": 8, "bid": 80},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.bid_max = int(p["bid"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.bids = [random.randint(1, self.bid_max) for _ in range(self.n)]
        if random.random() < 0.35:
            top = max(self.bids)
            j = random.randrange(self.n)
            self.bids[j] = top
        self.winner, self.payment = second_price(self.bids)
        self.answer = self.winner if self.task_type == "winner" else self.payment
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bids = ", ".join(f"({i + 1}, {b})" for i, b in enumerate(self.bids))
        rule = ((texts.t('s0', language)))
        ask = ((texts.t('s1', language) if self.task_type == "winner" else
                texts.t('s2', language)))
        return f"{rule} {((texts.t('s4', language)))}{bids}. {ask}"

    def solve(self):
        step = ((texts.t('s3', self.language, winner=self.winner, payment=self.payment)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
