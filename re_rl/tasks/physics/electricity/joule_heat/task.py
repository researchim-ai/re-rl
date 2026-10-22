"""JouleHeatTask — тепло Джоуля–Ленца, Q = I²Rt.

Ток, сопротивление и время — положительные целые, поэтому тепло целое.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class JouleHeatTask(BaseMathTask):
    TASK_TYPE = "joule_heat"
    TASK_TYPES = ["heat", "time", "current"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"i": 3, "r": 5, "t": 5},
        2: {"i": 4, "r": 6, "t": 6},
        3: {"i": 5, "r": 8, "t": 8},
        4: {"i": 6, "r": 10, "t": 10},
        5: {"i": 6, "r": 12, "t": 12},
        6: {"i": 8, "r": 12, "t": 15},
        7: {"i": 8, "r": 15, "t": 16},
        8: {"i": 10, "r": 16, "t": 18},
        9: {"i": 10, "r": 18, "t": 20},
        10: {"i": 12, "r": 20, "t": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.i = random.randint(1, int(p["i"]))
        self.r = random.randint(1, int(p["r"]))
        self.t = random.randint(1, int(p["t"]))
        self.heat = self.i * self.i * self.r * self.t
        self.square = self.i * self.i
        self.answer = {"heat": self.heat, "time": self.t, "current": self.i}[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "heat":
            return texts.t("s0", language, i=self.i, r=self.r, t=self.t)
        if self.task_type == "time":
            return texts.t("s1", language, heat=self.heat, i=self.i, r=self.r)
        return texts.t("s2", language, heat=self.heat, r=self.r, t=self.t)

    def solve(self):
        if self.task_type == "heat":
            step = texts.t("s3", self.language, i=self.i, r=self.r, t=self.t, heat=self.heat)
        elif self.task_type == "time":
            step = texts.t("s4", self.language, heat=self.heat, i=self.i, r=self.r, time=self.t)
        else:
            step = texts.t("s5", self.language, heat=self.heat, r=self.r, t=self.t, square=self.square, i=self.i)
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
