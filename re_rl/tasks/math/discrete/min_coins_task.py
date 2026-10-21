"""MinCoinsTask — минимальное число монет для суммы.

В отличие от подтипа coin_change у dynamic_programming (там спрашивают число
способов), здесь нужен минимум монет. Номиналы всегда содержат 1, поэтому
сумма достижима. На высоких уровнях чаще попадаются системы, где жадный
выбор самой крупной монеты не оптимален.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class MinCoinsTask(BaseMathTask):
    TASK_TYPE = "min_coins"
    TASK_TYPES = ["min_count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"hi": 12}, 2: {"hi": 18}, 3: {"hi": 24}, 4: {"hi": 30}, 5: {"hi": 40},
        6: {"hi": 50}, 7: {"hi": 60}, 8: {"hi": 80}, 9: {"hi": 100}, 10: {"hi": 120},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.hi = int(p["hi"])
        self.difficulty = difficulty
        self.task_type = "min_count"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @staticmethod
    def reconstruct(amount: int, coins: List[int]) -> Tuple[int, List[int]]:
        inf = amount + 1
        dp = [0] + [inf] * amount
        take = [-1] * (amount + 1)
        for s in range(1, amount + 1):
            for c in coins:
                if c <= s and dp[s - c] + 1 < dp[s]:
                    dp[s] = dp[s - c] + 1
                    take[s] = c
        combo = []
        s = amount
        while s > 0:
            c = take[s]
            combo.append(c)
            s -= c
        return dp[amount], combo

    @staticmethod
    def greedy_count(amount: int, coins: List[int]) -> int:
        left = amount
        cnt = 0
        for c in sorted(coins, reverse=True):
            cnt += left // c
            left %= c
        return cnt

    def _choose_coins(self) -> List[int]:
        if self.difficulty >= 5 and random.random() < 0.75:
            families = [
                [1, 3, 4],
                [1, 4, 6],
                [1, 5, 6],
                [1, 3, 5, 6],
                [1, 4, 5],
                [1, 6, 10, 15],
            ]
            return list(random.choice(families))
        k = 2 + self.difficulty // 4
        base = [1, 5, 10, 25]
        return base[:max(2, min(k, len(base)))]

    def _build(self):
        self.coins = self._choose_coins()
        lo = max(self.coins)
        hi = max(lo + 1, self.hi)
        self.amount = random.randint(lo, hi)
        if self.difficulty >= 5:
            for _ in range(40):
                amt = random.randint(lo, hi)
                opt, _ = self.reconstruct(amt, self.coins)
                if self.greedy_count(amt, self.coins) != opt:
                    self.amount = amt
                    break
        self.answer, self.combo = self.reconstruct(self.amount, self.coins)
        self.greedy = self.greedy_count(self.amount, self.coins)

    def _descr(self, language):
        ru = language == "ru"
        coins = ", ".join(map(str, self.coins))
        return ((f"Монеты номиналов {coins}, каждого номинала сколько угодно. Какое минимальное "
                 f"число монет нужно, чтобы набрать сумму {self.amount}?") if ru else
                (f"Coins of denominations {coins} are unlimited. What is the minimum number of coins "
                 f"needed to make {self.amount}?"))

    def solve(self):
        ru = self.language == "ru"
        combo = "+".join(map(str, sorted(self.combo, reverse=True)))
        if self.greedy == self.answer:
            greedy = ("Жадный выбор самых крупных монет даёт тот же минимум." if ru else
                      "Greedy selection of the largest coins gives the same minimum.")
        else:
            greedy = ((f"Жадный выбор самых крупных монет даёт {self.greedy}, это больше оптимума.")
                      if ru else
                      (f"Greedy selection of the largest coins uses {self.greedy}, which is worse "
                       f"than optimal."))
        self.solution_steps = [
            ((f"Одна оптимальная комбинация: {combo} ({self.answer} шт.).") if ru else
             (f"One optimal combination: {combo} ({self.answer} coins).")),
            greedy,
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
