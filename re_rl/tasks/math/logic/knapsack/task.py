"""Задачи комбинаторной оптимизации: рюкзак 0/1 и сумма подмножества."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

class KnapsackTask(BaseMathTask):
    TASK_TYPE = "knapsack"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "wmax": 6, "vmax": 8}, 2: {"n": 4, "wmax": 7, "vmax": 9},
        3: {"n": 4, "wmax": 8, "vmax": 10}, 4: {"n": 5, "wmax": 9, "vmax": 12},
        5: {"n": 6, "wmax": 10, "vmax": 15}, 6: {"n": 7, "wmax": 12, "vmax": 15},
        7: {"n": 8, "wmax": 12, "vmax": 20}, 8: {"n": 9, "wmax": 15, "vmax": 20},
        9: {"n": 10, "wmax": 15, "vmax": 25}, 10: {"n": 12, "wmax": 18, "vmax": 30},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.wmax, self.vmax = int(p["n"]), int(p["wmax"]), int(p["vmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.weights = [random.randint(1, self.wmax) for _ in range(self.n)]
        self.values = [random.randint(1, self.vmax) for _ in range(self.n)]
        total = sum(self.weights)
        low = min(self.wmax, total)
        self.capacity = random.randint(low, total)
        self._answer = self._solve_dp()

    def _solve_dp(self):
        cap = self.capacity
        dp = [0] * (cap + 1)
        for w, v in zip(self.weights, self.values):
            for c in range(cap, w - 1, -1):
                dp[c] = max(dp[c], dp[c - w] + v)
        return dp[cap]

    def _descr(self, language):
        items = "; ".join(texts.t('s3', language, v0=i + 1, v1=self.weights[i], v2=self.values[i])
                          for i in range(self.n))
        return ((texts.t('s0', language, capacity=self.capacity, items=items)))

    def solve(self):
        self.solution_steps = [
            texts.t("literals.s1", self.language),
            ((texts.t('s2', self.language, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
