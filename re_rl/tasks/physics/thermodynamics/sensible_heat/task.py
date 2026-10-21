"""SensibleHeatTask — количество теплоты Q = c * m * ΔT.

Все три множителя целые и положительные, поэтому любая из величин восстанавливается нацело.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def heat_quantity(specific: int, mass: int, delta: int) -> int:
    return specific * mass * delta


class SensibleHeatTask(BaseMathTask):
    TASK_TYPE = "sensible_heat"
    TASK_TYPES = ["heat", "mass", "specific_heat"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 5}, 2: {"m": 6}, 3: {"m": 6}, 4: {"m": 8}, 5: {"m": 8},
        6: {"m": 10}, 7: {"m": 10}, 8: {"m": 12}, 9: {"m": 14}, 10: {"m": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.specific = random.randint(1, limit)
        self.mass = random.randint(1, limit)
        self.delta = random.randint(1, limit)
        self.heat = heat_quantity(self.specific, self.mass, self.delta)
        self.answer = {
            "heat": self.heat,
            "mass": self.mass,
            "specific_heat": self.specific,
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        if self.task_type == "heat":
            ask = ((texts.t('s2', language, specific=self.specific, mass=self.mass, delta=self.delta)))
        elif self.task_type == "mass":
            ask = ((texts.t('s3', language, heat=self.heat, specific=self.specific, delta=self.delta)))
        else:
            ask = ((texts.t('s4', language, heat=self.heat, mass=self.mass, delta=self.delta)))
        return f"{law} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, specific=self.specific, mass=self.mass, delta=self.delta, heat=self.heat)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
