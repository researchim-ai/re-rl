"""MatrixChainTask — минимальная стоимость перемножения цепочки матриц.

Матрица i имеет размер dims[i] x dims[i+1]. Стоимость произведения
(p x q) на (q x r) равна p*q*r. Ответ — минимум по всем расстановкам скобок.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def matrix_chain_cost(dims: List[int]) -> int:
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            best = None
            for k in range(i, j):
                val = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if best is None or val < best:
                    best = val
            dp[i][j] = best
    return dp[0][n - 1]


class MatrixChainTask(BaseMathTask):
    TASK_TYPE = "matrix_chain"
    TASK_TYPES = ["cost"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "dim": 6}, 2: {"n": 3, "dim": 6}, 3: {"n": 3, "dim": 8},
        4: {"n": 4, "dim": 8}, 5: {"n": 4, "dim": 9}, 6: {"n": 5, "dim": 9},
        7: {"n": 5, "dim": 10}, 8: {"n": 6, "dim": 8}, 9: {"n": 6, "dim": 9},
        10: {"n": 7, "dim": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.dim = int(p["dim"])
        self.task_type = "cost"
        self.augment = augment
        self.dims = [random.randint(2, self.dim) for _ in range(self.n + 1)]
        self.answer = matrix_chain_cost(self.dims)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _sizes(self) -> str:
        return ", ".join(f"{self.dims[i]}x{self.dims[i + 1]}" for i in range(self.n))

    def _descr(self, language):
        ru = language == "ru"
        sizes = self._sizes()
        return ((f"Нужно перемножить матрицы {sizes} именно в этом порядке. "
                 f"Произведение матриц p x q и q x r стоит p*q*r скалярных умножений. "
                 f"Найдите минимальную стоимость по всем расстановкам скобок.") if ru else
                (f"Multiply the matrices {sizes} in this order. "
                 f"Multiplying a p x q matrix by a q x r matrix costs p*q*r scalar multiplications. "
                 f"Find the minimum cost over all parenthesizations."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Динамика по длине цепочки даёт стоимость {self.answer}.") if ru else
             (f"The length-based DP gives cost {self.answer}.")),
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
