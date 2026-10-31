"""ManhattanPathsTask — кратчайшие пути по клетке только вправо и вверх.

Длина равна x + y. Число путей равно C(x + y, x).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


class ManhattanPathsTask(BaseMathTask):
    TASK_TYPE = "manhattan_paths"
    TASK_TYPES = ["distance", "paths"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 4}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.x = random.randint(0, limit)
        self.y = random.randint(0, limit)
        if self.x == 0 and self.y == 0:
            self.x = 1
        self.distance = self.x + self.y
        self.paths = binom(self.distance, self.x)
        self.answer = self.distance if self.task_type == "distance" else self.paths
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "distance" else "s1"
        return texts.t(key, language, x=self.x, y=self.y)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "distance":
            step = texts.t("s2", self.language, x=self.x, y=self.y, answer=self.distance)
        else:
            step = texts.t("s3", self.language, steps=self.distance, x=self.x, answer=self.paths)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
