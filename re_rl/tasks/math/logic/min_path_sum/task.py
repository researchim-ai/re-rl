"""MinPathSumTask — минимальная сумма пути по сетке только вправо и вниз."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def min_path_sum(grid: List[List[int]]) -> int:
    cols = len(grid[0])
    dp = [0] * cols
    dp[0] = grid[0][0]
    for col in range(1, cols):
        dp[col] = dp[col - 1] + grid[0][col]
    for row in grid[1:]:
        dp[0] += row[0]
        for col in range(1, cols):
            dp[col] = min(dp[col], dp[col - 1]) + row[col]
    return dp[-1]


class MinPathSumTask(BaseMathTask):
    TASK_TYPE = texts.literal('literals.s2')
    TASK_TYPES = ["sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rows": 2, "cols": 2, "mag": 5}, 2: {"rows": 2, "cols": 3, "mag": 6},
        3: {"rows": 2, "cols": 3, "mag": 8}, 4: {"rows": 3, "cols": 3, "mag": 8},
        5: {"rows": 3, "cols": 3, "mag": 9}, 6: {"rows": 3, "cols": 4, "mag": 9},
        7: {"rows": 3, "cols": 4, "mag": 12}, 8: {"rows": 4, "cols": 4, "mag": 9},
        9: {"rows": 4, "cols": 4, "mag": 12}, 10: {"rows": 4, "cols": 5, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.rows = int(p["rows"])
        self.cols = int(p["cols"])
        self.mag = int(p["mag"])
        self.task_type = "sum"
        self.augment = augment
        self.grid = [[random.randint(1, self.mag) for _ in range(self.cols)] for _ in range(self.rows)]
        self.answer = min_path_sum(self.grid)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _grid_text(self) -> str:
        return " / ".join(" ".join(map(str, row)) for row in self.grid)

    def _descr(self, language):
        return ((texts.t('s0', language, v0=self._grid_text())))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
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
