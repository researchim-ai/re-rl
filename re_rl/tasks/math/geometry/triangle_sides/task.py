"""TriangleSidesTask — неравенство треугольника.

Подтип possible отвечает да/нет. Подтип max_side просит наибольшую целую третью сторону.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def is_triangle(a: int, b: int, c: int) -> bool:
    return a + b > c and a + c > b and b + c > a


class TriangleSidesTask(BaseMathTask):
    TASK_TYPE = "triangle_sides"
    TASK_TYPES = ["possible", "max_side"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 8}, 2: {"n": 10}, 3: {"n": 12}, 4: {"n": 15}, 5: {"n": 20},
        6: {"n": 25}, 7: {"n": 30}, 8: {"n": 40}, 9: {"n": 50}, 10: {"n": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.a = random.randint(1, limit)
        self.b = random.randint(1, limit)
        self.max_side = self.a + self.b - 1
        if self.task_type == "max_side":
            self.c = self.max_side
            self.possible = True
            self.answer = self.max_side
        else:
            self.possible = random.choice([True, False])
            if self.possible:
                low = abs(self.a - self.b) + 1
                self.c = random.randint(low, self.a + self.b - 1)
            else:
                self.c = self.a + self.b + random.randint(0, limit)
            self.answer = self.possible
        self.language = language
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _word(self, language, truth: bool) -> str:
        return texts.t("s4" if truth else "s5", language)

    def _descr(self, language):
        if self.task_type == "possible":
            return texts.t("s0", language, a=self.a, b=self.b, c=self.c)
        return texts.t("s1", language, a=self.a, b=self.b)

    def solve(self):
        if self.task_type == "possible":
            step = texts.t(
                "s2", self.language, a=self.a, b=self.b, c=self.c,
                ab=self.a + self.b, ac=self.a + self.c, bc=self.b + self.c,
                verdict=self._word(self.language, self.possible),
            )
            shown = self._word(self.language, self.possible)
        else:
            step = texts.t("s3", self.language, a=self.a, b=self.b, answer=self.max_side)
            shown = str(self.max_side)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=shown)]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "possible":
            return U.verify_bool(prediction, self.possible)
        return U.verify_int(prediction, self.max_side)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
