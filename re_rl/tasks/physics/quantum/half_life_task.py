"""HalfLifeStepsTask — дискретное деление пополам за каждый период полураспада.

Начальное количество делится на 2^k. Числа подобраны так, что ответ целый.

Подтипы: оставшиеся ядра, активность и число прошедших периодов.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HalfLifeStepsTask(BaseMathTask):
    TASK_TYPE = "half_life_steps"
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
        ru = language == "ru"
        rule = (("За каждый период полураспада количество и активность делятся ровно на 2.") if ru else
                ("Each half-life divides both the number of nuclei and the activity by exactly 2."))
        if self.task_type == "remaining":
            ask = ((f"Было {self.n0} ядер. Сколько останется через {self.k} периода полураспада?") if ru else
                   (f"There were {self.n0} nuclei. How many remain after {self.k} half-lives?"))
        elif self.task_type == "activity":
            ask = ((f"Начальная активность {self.activity0}. Какая активность будет через {self.k} "
                    f"периода полураспада?") if ru else
                   (f"The initial activity is {self.activity0}. What is the activity after {self.k} half-lives?"))
        else:
            ask = ((f"Число ядер уменьшилось с {self.n0} до {self.remaining}. "
                    f"Сколько периодов полураспада прошло?") if ru else
                   (f"The number of nuclei fell from {self.n0} to {self.remaining}. "
                    f"How many half-lives passed?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"{self.n0} / 2^{self.k} = {self.remaining} ядер, "
                 f"активность {self.activity0} / 2^{self.k} = {self.activity}.") if ru else
                (f"{self.n0} / 2^{self.k} = {self.remaining} nuclei, "
                 f"activity {self.activity0} / 2^{self.k} = {self.activity}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
