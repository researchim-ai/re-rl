"""GreedyCoinsTask — набор монет жадным правилом, а не минимумом.

Номиналы 1, 3 и 4. На каждом шаге берётся наибольшая монета, которая не больше остатка.
Для суммы 6 жадный набор 4+1+1 длиннее оптимального 3+3, поэтому минимум здесь не подходит.
Число монет в жадном наборе растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

DENOMS = (4, 3, 1)


def greedy_picks(amount: int) -> List[int]:
    picks = []
    left = amount
    while left:
        coin = max(item for item in DENOMS if item <= left)
        picks.append(coin)
        left -= coin
    return picks


def optimal_count(amount: int) -> int:
    best = [0] + [amount + 1] * amount
    for value in range(1, amount + 1):
        best[value] = 1 + min(best[value - coin] for coin in DENOMS if coin <= value)
    return best[amount]


class GreedyCoinsTask(BaseMathTask):
    TASK_TYPE = "greedy_coins"
    TASK_TYPES = ["count", "extra"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"g": 0}, 2: {"g": 0}, 3: {"g": 1}, 4: {"g": 1}, 5: {"g": 2},
        6: {"g": 3}, 7: {"g": 4}, 8: {"g": 5}, 9: {"g": 6}, 10: {"g": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        groups = int(p["g"]) + random.randint(0, 2)
        self.amount = 4 * groups + 6
        self.picks = greedy_picks(self.amount)
        self.n = len(self.picks)
        self.optimal = optimal_count(self.amount)
        self.extra = self.n - self.optimal
        self.answer = self.n if self.task_type == "count" else self.extra
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, amount=self.amount)

    def solve(self):
        steps = []
        left = self.amount
        for index, coin in enumerate(self.picks, 1):
            left -= coin
            steps.append(texts.t("s2", self.language, i=index, coin=coin, left=left))
        steps.append(texts.t("s3", self.language, greedy=self.n, optimal=self.optimal, extra=self.extra))
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
