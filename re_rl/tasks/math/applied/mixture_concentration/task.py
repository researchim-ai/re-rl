"""MixtureConcentrationTask — концентрация смеси двух растворов.

Объёмы и проценты подбираются так, чтобы концентрация смеси была целым числом.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _mixture(limit: int) -> Tuple[int, int, int, int, int]:
    for _ in range(80):
        v1 = random.randint(1, limit)
        v2 = random.randint(1, limit)
        c1 = random.randint(0, 100)
        c2 = random.randint(0, 100)
        total = v1 + v2
        amount = c1 * v1 + c2 * v2
        if amount % total == 0:
            return v1, c1, v2, c2, amount // total
    return 1, 20, 1, 20, 20


class MixtureConcentrationTask(BaseMathTask):
    TASK_TYPE = "mixture_concentration"
    TASK_TYPES = ["result", "second"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 4}, 2: {"v": 6}, 3: {"v": 8}, 4: {"v": 10}, 5: {"v": 12},
        6: {"v": 16}, 7: {"v": 20}, 8: {"v": 24}, 9: {"v": 30}, 10: {"v": 40},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.v1, self.c1, self.v2, self.c2, self.result = _mixture(int(p["v"]))
        self.answer = self.result if self.task_type == "result" else self.c2
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "result":
            return texts.t("s0", language, v1=self.v1, c1=self.c1, v2=self.v2, c2=self.c2)
        return texts.t("s1", language, result=self.result, v1=self.v1, c1=self.c1, v2=self.v2)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "result":
            step = texts.t("s2", self.language, c1=self.c1, v1=self.v1, c2=self.c2, v2=self.v2, result=self.result)
        else:
            step = texts.t("s3", self.language, result=self.result, v1=self.v1, v2=self.v2, c1=self.c1, c2=self.c2)
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
