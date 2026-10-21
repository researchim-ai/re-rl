"""FourierConductionTask — стационарный тепловой поток по закону Фурье.

H = k * A * dT / d. Толщина подбирается так, чтобы поток или толщина были целыми.

Подтипы: поток тепла и толщина стенки.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class FourierConductionTask(BaseMathTask):
    TASK_TYPE = "fourier_conduction"
    TASK_TYPES = ["rate", "thickness"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 4}, 2: {"m": 5}, 3: {"m": 6}, 4: {"m": 6}, 5: {"m": 8},
        6: {"m": 8}, 7: {"m": 10}, 8: {"m": 10}, 9: {"m": 12}, 10: {"m": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.k = random.randint(1, limit)
        self.area = random.randint(1, limit)
        self.delta = random.randint(1, limit)
        self.thickness = random.randint(1, limit)
        product = self.k * self.area * self.delta
        # Делаем поток целым: толщина — делитель произведения.
        divisors = [d for d in range(1, product + 1) if product % d == 0 and d <= max(limit, 1)]
        self.thickness = random.choice(divisors)
        self.rate = product // self.thickness
        self.answer = self.rate if self.task_type == "rate" else self.thickness
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        if self.task_type == "rate":
            ask = ((texts.t('s2', language, k=self.k, area=self.area, delta=self.delta, thickness=self.thickness)))
        else:
            ask = ((texts.t('s3', language, k=self.k, area=self.area, delta=self.delta, rate=self.rate)))
        return f"{law} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, k=self.k, area=self.area, delta=self.delta, thickness=self.thickness, rate=self.rate)))
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
