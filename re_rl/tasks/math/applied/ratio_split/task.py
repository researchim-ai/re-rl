"""RatioSplitTask — деление целой величины в заданном отношении.

Доли a:b и сама величина кратны a+b, поэтому обе части целые.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RatioSplitTask(BaseMathTask):
    TASK_TYPE = "ratio_split"
    TASK_TYPES = ["first", "second"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 6}, 3: {"n": 8}, 4: {"n": 10}, 5: {"n": 12},
        6: {"n": 15}, 7: {"n": 18}, 8: {"n": 20}, 9: {"n": 24}, 10: {"n": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.a = random.randint(1, limit)
        self.b = random.randint(1, limit)
        self.k = random.randint(1, limit)
        self.first = self.a * self.k
        self.second = self.b * self.k
        self.total = self.first + self.second
        self.answer = self.first if self.task_type == "first" else self.second
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "first" else "s1"
        return texts.t(key, language, total=self.total, a=self.a, b=self.b)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = texts.t(
            "s2", self.language, a=self.a, b=self.b, sum_ab=self.a + self.b,
            total=self.total, k=self.k, first=self.first, second=self.second,
        )
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
