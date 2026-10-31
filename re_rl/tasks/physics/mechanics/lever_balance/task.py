"""LeverBalanceTask — равновесие рычага: m1·d1 = m2·d2.

Плечи и массы подбираются так, чтобы неизвестная величина была целой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class LeverBalanceTask(BaseMathTask):
    TASK_TYPE = "lever_balance"
    TASK_TYPES = ["mass", "distance"]

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
        self.m1 = random.randint(1, limit)
        self.d1 = random.randint(1, limit)
        product = self.m1 * self.d1
        divisors = [item for item in range(1, limit + 1) if product % item == 0]
        self.m2 = random.choice(divisors)
        self.d2 = product // self.m2
        self.answer = self.m2 if self.task_type == "mass" else self.d2
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "mass":
            return texts.t("s0", language, m1=self.m1, d1=self.d1, d2=self.d2)
        return texts.t("s1", language, m1=self.m1, d1=self.d1, m2=self.m2)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = texts.t("s2", self.language, m1=self.m1, d1=self.d1, m2=self.m2, d2=self.d2)
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
