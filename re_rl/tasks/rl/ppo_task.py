"""PpoClipTask — обрезка отношения вероятностей в PPO.

r ограничивается отрезком от 1-ε до 1+ε.
Суррогат — минимум из r*A и (обрезанное r)*A. Знак A учитывается этим минимумом.
"""

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
        ru = language == "ru"
        rule = ((f"PPO. Отношение вероятностей r = {fmt_fraction(self.ratio)} обрезается "
                 f"в отрезок от 1 - ε до 1 + ε, ε = {fmt_fraction(self.epsilon)}. "
                 f"Суррогат — меньшее из r * A и (обрезанное r) * A, A = {self.advantage}. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"PPO. The probability ratio r = {fmt_fraction(self.ratio)} is clipped "
                 f"to the segment from 1 - ε to 1 + ε, ε = {fmt_fraction(self.epsilon)}. "
                 f"The surrogate is the smaller of r * A and (clipped r) * A, A = {self.advantage}. "
                 f"Answer with an integer or a reduced fraction."))
        ask = (("Найдите обрезанное отношение." if ru else "Find the clipped ratio.")
               if self.task_type == "clipped" else
               ("Найдите суррогат." if ru else "Find the surrogate."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Обрезанное r = {fmt_fraction(self.clipped)}, суррогат = {fmt_fraction(self.surrogate)}.")
                if ru else
                (f"Clipped r = {fmt_fraction(self.clipped)}, surrogate = {fmt_fraction(self.surrogate)}."))
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
