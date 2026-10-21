"""HalfLifeStepsTask — дискретное деление пополам за каждый период полураспада.

Начальное количество делится на 2^k. Числа подобраны так, что ответ целый.

Подтипы: оставшиеся ядра, активность и число прошедших периодов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HalfLifeStepsTask(BaseMathTask):
    TASK_TYPE = texts.literal('literals.s5')
    TASK_TYPES = ["remaining", "activity", "periods"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 2, "base": 4}, 2: {"k": 3, "base": 5}, 3: {"k": 3, "base": 6},
        4: {"k": 4, "base": 6}, 5: {"k": 4, "base": 8}, 6: {"k": 5, "base": 8},
        7: {"k": 5, "base": 10}, 8: {"k": 6, "base": 8}, 9: {"k": 6, "base": 10},
        10: {"k": 8, "base": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.kmax = int(p["k"])
        self.base_max = int(p["base"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.k = random.randint(1, self.kmax)
        self.base = random.randint(1, self.base_max)
        self.n0 = self.base * (1 << self.k)
        self.remaining = self.base
        self.activity0 = random.randint(1, self.base_max) * (1 << self.k)
        self.activity = self.activity0 >> self.k
        if self.task_type == "remaining":
            self.answer = self.remaining
        elif self.task_type == "activity":
            self.answer = self.activity
        else:
            self.answer = self.k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "remaining":
            ask = ((texts.t('s2', language, n0=self.n0, k=self.k)))
        elif self.task_type == "activity":
            ask = ((texts.t('s3', language, activity0=self.activity0, k=self.k)))
        else:
            ask = ((texts.t('s4', language, n0=self.n0, remaining=self.remaining)))
        return f"{rule} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, n0=self.n0, k=self.k, remaining=self.remaining, activity0=self.activity0, k_2=self.k, activity=self.activity)))
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
