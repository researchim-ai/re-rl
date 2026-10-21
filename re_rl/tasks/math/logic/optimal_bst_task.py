"""OptimalBstTask — минимальная стоимость дерева поиска.

Корень имеет глубину 1. Стоимость — сумма частот ключей, умноженных на их глубину.
Ключи уже стоят по возрастанию, даны только частоты.
"""

import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def optimal_bst(freq: Sequence[int]) -> int:
    n = len(freq)
    prefix = [0]
    for value in freq:
        prefix.append(prefix[-1] + value)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = freq[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            weight = prefix[j + 1] - prefix[i]
            best = None
            for root in range(i, j + 1):
                left = dp[i][root - 1] if root > i else 0
                right = dp[root + 1][j] if root < j else 0
                cand = weight + left + right
                if best is None or cand < best:
                    best = cand
            dp[i][j] = best
    return dp[0][n - 1]


class OptimalBstTask(BaseMathTask):
    TASK_TYPE = "optimal_bst"
    TASK_TYPES = ["cost"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 4}, 2: {"n": 3, "mag": 5}, 3: {"n": 4, "mag": 5},
        4: {"n": 4, "mag": 6}, 5: {"n": 5, "mag": 6}, 6: {"n": 5, "mag": 7},
        7: {"n": 6, "mag": 7}, 8: {"n": 6, "mag": 8}, 9: {"n": 7, "mag": 8},
        10: {"n": 8, "mag": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "cost"
        self.augment = augment
        self.freq = [random.randint(1, self.mag) for _ in range(self.n)]
        self.answer = optimal_bst(self.freq)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.freq))
        return ((f"Ключи уже упорядочены. Их частоты слева направо: {data}. "
                 f"Корень дерева имеет глубину 1, дети корня — глубину 2 и так далее. "
                 f"Стоимость дерева — сумма частот, умноженных на глубину ключа. "
                 f"Найдите минимальную стоимость.") if ru else
                (f"The keys are already sorted. Their frequencies from left to right: {data}. "
                 f"The root has depth 1, the root's children have depth 2, and so on. "
                 f"The cost of a tree is the sum of frequency times key depth. "
                 f"Find the minimum cost."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Минимальная стоимость равна {self.answer}.") if ru else
                (f"The minimum cost is {self.answer}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
