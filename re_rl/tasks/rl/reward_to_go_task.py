"""RewardToGoTask — отдача с выбранного шага траектории.

G_t = r_t + γ r_{t+1} + ... до конца. Нумерация шагов с 0.
γ — дробь, ответ точный.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction
from re_rl.tasks.rl.discounted_return_task import discounted

_GAMMAS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


class RewardToGoTask(BaseMathTask):
    TASK_TYPE = "reward_to_go"
    TASK_TYPES = ["from_step"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 3}, 2: {"n": 3, "mag": 4}, 3: {"n": 4, "mag": 4},
        4: {"n": 4, "mag": 5}, 5: {"n": 5, "mag": 5}, 6: {"n": 5, "mag": 6},
        7: {"n": 6, "mag": 6}, 8: {"n": 6, "mag": 7}, 9: {"n": 7, "mag": 7},
        10: {"n": 8, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = "from_step"
        self.augment = augment
        self.gamma = random.choice(_GAMMAS[:1 + min(3, difficulty // 3)])
        self.rewards = [random.randint(-self.mag, self.mag) for _ in range(self.count)]
        self.t = random.randint(0, self.count - 1)
        self.answer = discounted(self.rewards[self.t:], self.gamma)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rewards = ", ".join(map(str, self.rewards))
        gamma = fmt_fraction(self.gamma)
        return ((f"Награды с шага 0: {rewards}. Дисконт γ = {gamma}. "
                 f"Найдите отдачу начиная с шага {self.t}: r_t + γ r_(t+1) + ... "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"Rewards from step 0: {rewards}. Discount γ = {gamma}. "
                 f"Find the return starting at step {self.t}: r_t + γ r_(t+1) + ... "
                 f"Answer with an integer or a reduced fraction."))

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Хвост наград с шага {self.t}: {', '.join(map(str, self.rewards[self.t:]))}. "
                 f"Отдача {shown}.") if ru else
                (f"Reward tail from step {self.t}: {', '.join(map(str, self.rewards[self.t:]))}. "
                 f"Return {shown}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
