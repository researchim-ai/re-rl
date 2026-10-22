"""PolygonAnglesTask — углы и диагонали выпуклого многоугольника.

Сумма внутренних углов и число диагоналей целые для любого n ≥ 3.
Один угол правильного n-угольника спрашивается только когда он целый.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_INTEGER_ANGLE = [3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 72, 90, 120]


class PolygonAnglesTask(BaseMathTask):
    TASK_TYPE = "polygon_angles"
    TASK_TYPES = ["sum", "angle", "diagonals"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 8}, 3: {"n": 10}, 4: {"n": 12}, 5: {"n": 15},
        6: {"n": 18}, 7: {"n": 24}, 8: {"n": 30}, 9: {"n": 36}, 10: {"n": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = max(3, int(p["n"]))
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        if self.task_type == "angle":
            choices = [n for n in _INTEGER_ANGLE if 3 <= n <= limit] or [3, 4, 6]
            self.n = random.choice(choices)
        else:
            self.n = random.randint(3, limit)
        self.sum = (self.n - 2) * 180
        self.angle = self.sum // self.n
        self.diagonals = self.n * (self.n - 3) // 2
        self.answer = {"sum": self.sum, "angle": self.angle, "diagonals": self.diagonals}[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = {"sum": "s0", "angle": "s1", "diagonals": "s2"}[self.task_type]
        return texts.t(key, language, n=self.n)

    def solve(self):
        if self.task_type == "sum":
            step = texts.t("s3", self.language, n=self.n, nm2=self.n - 2, answer=self.sum)
        elif self.task_type == "angle":
            step = texts.t("s4", self.language, n=self.n, total=self.sum, answer=self.angle)
        else:
            step = texts.t("s5", self.language, n=self.n, nm3=self.n - 3, answer=self.diagonals)
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
