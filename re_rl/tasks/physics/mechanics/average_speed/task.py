"""AverageSpeedTask — средняя скорость на двух равных участках.

v = 2·v1·v2 / (v1 + v2). Пара скоростей выбирается так, чтобы ответ был целым.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _harmonic_pair(limit: int) -> Tuple[int, int, int]:
    equal: Optional[Tuple[int, int, int]] = None
    for _ in range(80):
        v1 = random.randint(1, limit)
        v2 = random.randint(1, limit)
        if (2 * v1 * v2) % (v1 + v2) != 0:
            continue
        average = (2 * v1 * v2) // (v1 + v2)
        if v1 != v2:
            return v1, v2, average
        equal = (v1, v2, average)
    return equal or (limit, limit, limit)


class AverageSpeedTask(BaseMathTask):
    TASK_TYPE = "average_speed"
    TASK_TYPES = ["average", "other_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 6}, 2: {"v": 8}, 3: {"v": 10}, 4: {"v": 12}, 5: {"v": 16},
        6: {"v": 20}, 7: {"v": 24}, 8: {"v": 30}, 9: {"v": 36}, 10: {"v": 48},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.v1, self.v2, self.average = _harmonic_pair(int(p["v"]))
        self.answer = self.average if self.task_type == "average" else self.v2
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "average":
            return texts.t("s0", language, v1=self.v1, v2=self.v2)
        return texts.t("s1", language, average=self.average, v1=self.v1)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "average":
            step = texts.t("s2", self.language, v1=self.v1, v2=self.v2, average=self.average)
        else:
            step = texts.t("s3", self.language, average=self.average, v1=self.v1, v2=self.v2)
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
