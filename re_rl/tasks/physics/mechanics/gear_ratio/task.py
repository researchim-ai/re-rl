"""GearRatioTask — зацепление двух шестерён.

Произведение числа зубьев на частоту вращения одинаково у ведущей и ведомой шестерни.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GearRatioTask(BaseMathTask):
    TASK_TYPE = "gear_ratio"
    TASK_TYPES = ["speed", "teeth"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 8}, 5: {"n": 8},
        6: {"n": 10}, 7: {"n": 12}, 8: {"n": 12}, 9: {"n": 16}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n1 = random.randint(1, limit)
        self.n2 = random.randint(1, limit)
        self.factor = random.randint(1, limit)
        self.w1 = self.n2 * self.factor
        self.w2 = self.n1 * self.factor
        self.answer = self.w2 if self.task_type == "speed" else self.n2
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "speed":
            return texts.t("s0", language, n1=self.n1, w1=self.w1, n2=self.n2)
        return texts.t("s1", language, n1=self.n1, w1=self.w1, w2=self.w2)

    def solve(self):
        step = texts.t("s2", self.language, n1=self.n1, w1=self.w1, n2=self.n2, w2=self.w2)
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
