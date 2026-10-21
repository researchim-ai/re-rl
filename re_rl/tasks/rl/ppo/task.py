"""PpoClipTask — обрезка отношения вероятностей в PPO.

r ограничивается отрезком от 1-ε до 1+ε.
Суррогат — минимум из r*A и (обрезанное r)*A. Знак A учитывается этим минимумом.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_EPSILONS = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 5)]


def ppo_clip(ratio: Fraction, epsilon: Fraction, advantage: int) -> Tuple[Fraction, Fraction]:
    clipped = min(max(ratio, 1 - epsilon), 1 + epsilon)
    surrogate = min(ratio * advantage, clipped * advantage)
    return clipped, surrogate


class PpoClipTask(BaseMathTask):
    TASK_TYPE = "ppo_clip"
    TASK_TYPES = ["clipped", "surrogate"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mag": 4}, 2: {"mag": 5}, 3: {"mag": 6}, 4: {"mag": 6}, 5: {"mag": 8},
        6: {"mag": 8}, 7: {"mag": 10}, 8: {"mag": 10}, 9: {"mag": 12}, 10: {"mag": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.epsilon = random.choice(_EPSILONS[:1 + min(2, difficulty // 4)])
        numer = random.randint(1, self.mag)
        denom = random.randint(1, self.mag)
        self.ratio = Fraction(numer, denom)
        self.advantage = random.randint(-self.mag, self.mag)
        self.clipped, self.surrogate = ppo_clip(self.ratio, self.epsilon, self.advantage)
        self.answer = self.clipped if self.task_type == "clipped" else self.surrogate
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language, v0=fmt_fraction(self.ratio), v1=fmt_fraction(self.epsilon), advantage=self.advantage)))
        ask = (((texts.t('s2', language)))
               if self.task_type == "clipped" else
               ((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, v0=fmt_fraction(self.clipped), v1=fmt_fraction(self.surrogate))))
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
