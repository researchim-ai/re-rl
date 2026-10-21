"""DynamicProgrammingTask — задачи, решаемые динамическим программированием.

Подтипы:
- ``grid_paths``: число путей в сетке из левого верхнего в правый нижний угол
  (движение только вправо/вниз).
- ``coin_change``: число способов набрать сумму монетами заданных номиналов.

Ответ — целое число, поэтому задача однозначно верифицируется.
"""

import math
import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class DynamicProgrammingTask(BaseMathTask):
    """Комбинаторные задачи на ДП (число путей / число разменов)."""

    TASK_TYPE = "dynamic_programming"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_dim": 3, "amount": 8, "num_coins": 2, "subtype": "grid_paths"},
        2: {"max_dim": 4, "amount": 10, "num_coins": 2, "subtype": "grid_paths"},
        3: {"max_dim": 5, "amount": 12, "num_coins": 3, "subtype": "grid_paths"},
        4: {"max_dim": 6, "amount": 15, "num_coins": 3, "subtype": "coin_change"},
        5: {"max_dim": 7, "amount": 18, "num_coins": 3, "subtype": "coin_change"},
        6: {"max_dim": 8, "amount": 22, "num_coins": 3, "subtype": "coin_change"},
        7: {"max_dim": 9, "amount": 26, "num_coins": 4, "subtype": "coin_change"},
        8: {"max_dim": 10, "amount": 30, "num_coins": 4, "subtype": "coin_change"},
        9: {"max_dim": 12, "amount": 35, "num_coins": 4, "subtype": "coin_change"},
        10: {"max_dim": 14, "amount": 40, "num_coins": 4, "subtype": "coin_change"},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        subtype: Optional[str] = None,
        max_dim: Optional[int] = None,
        amount: Optional[int] = None,
        num_coins: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or preset.get("subtype", "grid_paths")
        self.max_dim = int(max_dim if max_dim is not None else preset.get("max_dim", 5))
        self.amount = int(amount if amount is not None else preset.get("amount", 12))
        self.num_coins = int(num_coins if num_coins is not None else preset.get("num_coins", 3))
        self.augment = augment

        self.rows = 0
        self.cols = 0
        self.coins: List[int] = []

        if self.subtype == "grid_paths":
            self.rows = random.randint(2, self.max_dim)
            self.cols = random.randint(2, self.max_dim)
            description = get_template(
                PROMPT_TEMPLATES["dynamic_programming"], "grid_problem", language,
                augment=augment, rows=self.rows, cols=self.cols,
            )
        else:
            self.coins = self._make_coins()
            description = get_template(
                PROMPT_TEMPLATES["dynamic_programming"], "coin_problem", language,
                augment=augment, amount=self.amount, coins=", ".join(map(str, self.coins)),
            )

        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_coins(self) -> List[int]:
        candidates = [1, 2, 3, 5, 7, 10]
        coins = sorted(random.sample(candidates, min(self.num_coins, len(candidates))))
        if 1 not in coins:
            coins[0] = 1  # гарантируем существование хотя бы одного размена
            coins = sorted(set(coins))
        return coins

    @staticmethod
    def _count_grid_paths(rows: int, cols: int) -> int:
        return math.comb(rows + cols - 2, rows - 1)

    @staticmethod
    def _count_coin_change(amount: int, coins: List[int]) -> int:
        dp = [0] * (amount + 1)
        dp[0] = 1
        for coin in coins:
            for s in range(coin, amount + 1):
                dp[s] += dp[s - coin]
        return dp[amount]

    def solve(self):
        section = PROMPT_TEMPLATES["dynamic_programming"]
        if self.subtype == "grid_paths":
            result = self._count_grid_paths(self.rows, self.cols)
            self.solution_steps.append(
                get_template(section, "grid_step", self.language, augment=False,
                             rows=self.rows, cols=self.cols, result=result)
            )
        else:
            result = self._count_coin_change(self.amount, self.coins)
            self.solution_steps.append(
                get_template(section, "coin_step", self.language, augment=False, result=result)
            )
        self.solution_steps.append(
            get_template(section, "result", self.language, augment=False, result=result)
        )
        self.final_answer = str(result)

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "DynamicProgrammingTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
