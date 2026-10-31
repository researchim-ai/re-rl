"""MatrixChainTask — минимальная стоимость перемножения цепочки матриц.

Матрица i имеет размер dims[i] x dims[i+1]. Стоимость произведения
(p x q) на (q x r) равна p*q*r. Ответ — минимум по всем расстановкам скобок.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        sizes = self._sizes()
        return ((texts.t('s0', language, sizes=sizes)))

    def solve(self):
        from re_rl.tasks.math.algorithm_traces.solvers import solve_detailed
        solve_detailed(self)

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
