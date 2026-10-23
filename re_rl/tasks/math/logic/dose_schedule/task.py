"""DoseScheduleTask — уровень лекарства по дням.

Каждое утро остаток делится пополам с округлением вниз, затем добавляется доза этого дня.
Число дней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def concentration_trace(doses: Sequence[int]) -> Tuple[List[int], int]:
    level = 0
    peak = 0
    trace = []
    for dose in doses:
        level //= 2
        level += dose
        peak = max(peak, level)
        trace.append(level)
    return trace, peak


class DoseScheduleTask(BaseMathTask):
    TASK_TYPE = "dose_schedule"
    TASK_TYPES = ["level", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 4}, 2: {"n": 2, "m": 6}, 3: {"n": 3, "m": 6},
        4: {"n": 3, "m": 8}, 5: {"n": 4, "m": 8}, 6: {"n": 5, "m": 8},
        7: {"n": 6, "m": 10}, 8: {"n": 7, "m": 10}, 9: {"n": 8, "m": 10},
        10: {"n": 10, "m": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.doses = [random.randint(0, limit) for _ in range(self.n)]
        if sum(self.doses) == 0:
            self.doses[0] = 1
        self.levels, self.peak = concentration_trace(self.doses)
        self.level = self.levels[-1]
        self.answer = self.level if self.task_type == "level" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(dose) for dose in self.doses)
        key = "s0" if self.task_type == "level" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, dose=dose, level=level)
            for index, (dose, level) in enumerate(zip(self.doses, self.levels), 1)
        ]
        steps.append(texts.t("s3", self.language, level=self.level, peak=self.peak))
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
