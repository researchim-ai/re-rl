"""RewardClipTask — отдача после обрезки наград.

Каждая награда заменяется ближайшим числом из отрезка от -c до c.
Отдача обрезанной последовательности считается с дисконтом γ.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction
from re_rl.tasks.rl.discounted_return_task import discounted

_GAMMAS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


def clip_rewards(rewards: List[int], limit: int) -> List[int]:
    return [min(max(reward, -limit), limit) for reward in rewards]


class RewardClipTask(BaseMathTask):
    TASK_TYPE = "reward_clip"
    TASK_TYPES = ["clipped", "return"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 4, "c": 2}, 2: {"n": 3, "mag": 5, "c": 2},
        3: {"n": 4, "mag": 6, "c": 3}, 4: {"n": 4, "mag": 6, "c": 3},
        5: {"n": 4, "mag": 8, "c": 3}, 6: {"n": 5, "mag": 8, "c": 4},
        7: {"n": 5, "mag": 10, "c": 4}, 8: {"n": 6, "mag": 10, "c": 5},
        9: {"n": 6, "mag": 12, "c": 5}, 10: {"n": 7, "mag": 12, "c": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.limit = random.randint(1, int(p["c"]))
        self.rewards = [random.randint(-self.mag, self.mag) for _ in range(self.count)]
        self.gamma = random.choice(_GAMMAS[:1 + min(3, difficulty // 3)])
        self.t = random.randrange(self.count)
        self.clipped = clip_rewards(self.rewards, self.limit)
        self.ret = discounted(self.clipped, self.gamma)
        self.answer = Fraction(self.clipped[self.t]) if self.task_type == "clipped" else self.ret
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rewards = ", ".join(map(str, self.rewards))
        gamma = fmt_fraction(self.gamma)
        rule = ((f"Награды: {rewards}. Каждая заменяется ближайшим числом из отрезка от -{self.limit} до {self.limit}. "
                 f"Отдача — сумма уже обрезанных наград с дисконтом γ = {gamma}, начиная с первой. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"Rewards: {rewards}. Each is replaced by the nearest number in the segment from -{self.limit} to {self.limit}. "
                 f"The return sums the clipped rewards with discount γ = {gamma}, starting from the first. "
                 f"Answer with an integer or a reduced fraction."))
        ask = ((f"Найдите обрезанную награду шага {self.t}. Шаги нумеруются с 0." if ru else
                f"Find the clipped reward at step {self.t}. Steps start at 0.")
               if self.task_type == "clipped" else
               ("Найдите отдачу." if ru else "Find the return."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        clipped = ", ".join(map(str, self.clipped))
        step = ((f"После обрезки: {clipped}. Отдача {fmt_fraction(self.ret)}.") if ru else
                (f"After clipping: {clipped}. Return {fmt_fraction(self.ret)}."))
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
