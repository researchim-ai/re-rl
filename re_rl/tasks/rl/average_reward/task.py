"""AverageRewardTask — средняя награда и дифференциальная TD-ошибка.

R — среднее наград. δ_t = r_t - R + V_(t+1) - V_t.
Оценок V на одну больше, чем наград. Шаги нумеруются с 0.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def average_reward_parts(rewards: List[int], values: List[int], t: int) -> Tuple[Fraction, Fraction]:
    mean = Fraction(sum(rewards), len(rewards))
    delta = Fraction(rewards[t]) - mean + values[t + 1] - values[t]
    return mean, delta


class AverageRewardTask(BaseMathTask):
    TASK_TYPE = "average_reward"
    TASK_TYPES = ["mean", "delta"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 3}, 2: {"n": 2, "mag": 4}, 3: {"n": 3, "mag": 4},
        4: {"n": 3, "mag": 5}, 5: {"n": 4, "mag": 5}, 6: {"n": 4, "mag": 6},
        7: {"n": 5, "mag": 6}, 8: {"n": 5, "mag": 7}, 9: {"n": 6, "mag": 7},
        10: {"n": 6, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.count = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.rewards = [random.randint(0, self.mag) for _ in range(self.count)]
        self.values = [random.randint(-self.mag, self.mag) for _ in range(self.count + 1)]
        self.t = random.randrange(self.count)
        self.mean, self.delta = average_reward_parts(self.rewards, self.values, self.t)
        self.answer = self.mean if self.task_type == "mean" else self.delta
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rewards = ", ".join(map(str, self.rewards))
        values = ", ".join(map(str, self.values))
        rule = ((texts.t('s0', language)))
        data = ((texts.t('s1', language, rewards=rewards, values=values)))
        ask = (((texts.t('s2', language))) if self.task_type == "mean" else
               ((texts.t('s3', language, t=self.t))))
        return f"{rule} {data} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((f"R = {fmt_fraction(self.mean)}, δ_{self.t} = {fmt_fraction(self.delta)}."))
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
