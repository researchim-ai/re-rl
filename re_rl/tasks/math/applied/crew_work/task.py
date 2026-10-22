"""CrewWorkTask — бригада из нескольких работников.

Число работников растёт с уровнем. Объём заказа кратен их суммарной выработке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class CrewWorkTask(BaseMathTask):
    TASK_TYPE = "crew_work"
    TASK_TYPES = ["days"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "r": 5, "d": 4}, 2: {"n": 2, "r": 6, "d": 5},
        3: {"n": 3, "r": 6, "d": 6}, 4: {"n": 3, "r": 8, "d": 6},
        5: {"n": 4, "r": 8, "d": 8}, 6: {"n": 5, "r": 10, "d": 8},
        7: {"n": 6, "r": 10, "d": 10}, 8: {"n": 7, "r": 12, "d": 10},
        9: {"n": 8, "r": 12, "d": 12}, 10: {"n": 10, "r": 15, "d": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "days"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rates: List[int] = [random.randint(1, int(p["r"])) for _ in range(self.n)]
        self.days = random.randint(1, int(p["d"]))
        self.rate = sum(self.rates)
        self.job = self.days * self.rate
        self.answer = self.days
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [texts.t("s1", language, i=i, rate=rate) for i, rate in enumerate(self.rates, 1)]
        return texts.t("s0", language, n=self.n, crew=" ".join(parts), job=self.job)

    def solve(self):
        steps = [texts.t("s2", self.language, i=i, rate=rate) for i, rate in enumerate(self.rates, 1)]
        steps.append(texts.t("s3", self.language, rate=self.rate, job=self.job, days=self.days))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
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
