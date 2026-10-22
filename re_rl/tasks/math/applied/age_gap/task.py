"""AgeGapTask — разница возрастов и момент, когда старший становится вдвое старше младшего.

Возраст старшего равен 2·возраст младшего плюс число лет до этого момента.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class AgeGapTask(BaseMathTask):
    TASK_TYPE = "age_gap"
    TASK_TYPES = ["gap", "twice"]

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
        self.young = random.randint(1, limit)
        self.years = random.randint(1, limit)
        self.older = 2 * self.young + self.years
        self.gap = self.older - self.young
        self.answer = self.gap if self.task_type == "gap" else self.years
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "gap" else "s1"
        return texts.t(key, language, older=self.older, young=self.young)

    def solve(self):
        if self.task_type == "gap":
            step = texts.t("s2", self.language, older=self.older, young=self.young, gap=self.gap)
        else:
            step = texts.t("s3", self.language, older=self.older, young=self.young, years=self.years)
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
