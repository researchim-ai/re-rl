"""HookeLawTask — закон Гука для пружины, F = kx.

Жёсткость и удлинение — положительные целые, поэтому сила тоже целая.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HookeLawTask(BaseMathTask):
    TASK_TYPE = "hooke_law"
    TASK_TYPES = ["force", "extension", "stiffness"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 5, "x": 5}, 2: {"k": 8, "x": 6}, 3: {"k": 10, "x": 8},
        4: {"k": 12, "x": 10}, 5: {"k": 15, "x": 12}, 6: {"k": 20, "x": 12},
        7: {"k": 25, "x": 15}, 8: {"k": 30, "x": 18}, 9: {"k": 40, "x": 20},
        10: {"k": 50, "x": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.k = random.randint(1, int(p["k"]))
        self.x = random.randint(1, int(p["x"]))
        self.force = self.k * self.x
        self.answer = {"force": self.force, "extension": self.x, "stiffness": self.k}[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "force":
            return texts.t("s0", language, k=self.k, x=self.x)
        if self.task_type == "extension":
            return texts.t("s1", language, force=self.force, k=self.k)
        return texts.t("s2", language, force=self.force, x=self.x)

    def solve(self):
        if self.task_type == "force":
            step = texts.t("s3", self.language, k=self.k, x=self.x, force=self.force)
        elif self.task_type == "extension":
            step = texts.t("s4", self.language, force=self.force, k=self.k, x=self.x)
        else:
            step = texts.t("s5", self.language, force=self.force, x=self.x, k=self.k)
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
