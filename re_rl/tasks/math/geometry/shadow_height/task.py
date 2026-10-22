"""ShadowHeightTask — высота по подобным теням.

Отношение высоты к длине тени одно и то же, числа подобраны так, чтобы ответ был целым.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class ShadowHeightTask(BaseMathTask):
    TASK_TYPE = "shadow_height"
    TASK_TYPES = ["pole", "stick_shadow"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 8}, 5: {"n": 8},
        6: {"n": 10}, 7: {"n": 12}, 8: {"n": 12}, 9: {"n": 15}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.stick = random.randint(1, limit)
        self.stick_shadow = random.randint(1, limit)
        self.scale = random.randint(1, limit)
        self.pole = self.stick * self.scale
        self.pole_shadow = self.stick_shadow * self.scale
        self.answer = self.pole if self.task_type == "pole" else self.stick_shadow
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "pole":
            return texts.t(
                "s0", language, stick=self.stick, stick_shadow=self.stick_shadow,
                pole_shadow=self.pole_shadow,
            )
        return texts.t(
            "s1", language, pole=self.pole, pole_shadow=self.pole_shadow, stick=self.stick,
        )

    def solve(self):
        step = texts.t(
            "s2", self.language, stick=self.stick, stick_shadow=self.stick_shadow,
            pole=self.pole, pole_shadow=self.pole_shadow,
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
