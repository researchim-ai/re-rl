"""RewardToGoTask — отдача с выбранного шага траектории.

G_t = r_t + γ r_{t+1} + ... до конца. Нумерация шагов с 0.
γ — дробь, ответ точный.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction
from re_rl.tasks.rl.discounted_return_task import discounted

_GAMMAS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


class RewardToGoTask(BaseMathTask):
    TASK_TYPE = texts.literal('literals.s2')
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
        rewards = ", ".join(map(str, self.rewards))
        gamma = fmt_fraction(self.gamma)
        return ((texts.t('s0', language, rewards=rewards, gamma=gamma, t=self.t)))

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, t=self.t, v1=', '.join(map(str, self.rewards[self.t:])), shown=shown)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
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
