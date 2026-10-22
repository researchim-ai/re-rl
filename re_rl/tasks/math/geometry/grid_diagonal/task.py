"""GridDiagonalTask — диагональ прямоугольника из единичных клеток.

Число пересечённых клеток равно m + n − gcd(m, n).
Число узлов строго внутри диагонали равно gcd(m, n) − 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GridDiagonalTask(BaseMathTask):
    TASK_TYPE = "grid_diagonal"
    TASK_TYPES = ["squares", "interior"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 8}, 3: {"n": 10}, 4: {"n": 12}, 5: {"n": 15},
        6: {"n": 18}, 7: {"n": 20}, 8: {"n": 24}, 9: {"n": 30}, 10: {"n": 36},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.m = random.randint(1, limit)
        self.n = random.randint(1, limit)
        self.g = math.gcd(self.m, self.n)
        self.squares = self.m + self.n - self.g
        self.interior = self.g - 1
        self.answer = self.squares if self.task_type == "squares" else self.interior
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "squares" else "s1"
        return texts.t(key, language, m=self.m, n=self.n)

    def solve(self):
        if self.task_type == "squares":
            step = texts.t("s2", self.language, m=self.m, n=self.n, g=self.g, answer=self.squares)
        else:
            step = texts.t("s3", self.language, g=self.g, answer=self.interior)
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
