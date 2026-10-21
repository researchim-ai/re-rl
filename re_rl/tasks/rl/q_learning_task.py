"""QLearningTask — одно обновление Q-learning.

δ = r + γ * max_next - Q
Q_new = Q + α * δ
α и γ — дроби 1 или 1/2, остальные величины целые, результат — точная дробь.

Подтипы: новая оценка Q и сама TD-ошибка δ.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def q_update(q: int, alpha: Fraction, reward: int, gamma: Fraction, max_next: int):
    delta = reward + gamma * max_next - q
    return q + alpha * delta, delta


class QLearningTask(BaseMathTask):
    TASK_TYPE = "q_learning"
    TASK_TYPES = ["q_new", "td_error"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mag": 3}, 2: {"mag": 4}, 3: {"mag": 5}, 4: {"mag": 6}, 5: {"mag": 6},
        6: {"mag": 8}, 7: {"mag": 8}, 8: {"mag": 10}, 9: {"mag": 12}, 10: {"mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.q = random.randint(-self.mag, self.mag)
        self.reward = random.randint(-self.mag, self.mag)
        self.max_next = random.randint(-self.mag, self.mag)
        self.alpha = Fraction(1, 1) if difficulty < 4 or random.random() < 0.5 else Fraction(1, 2)
        self.gamma = Fraction(1, 1) if difficulty < 3 or random.random() < 0.5 else Fraction(1, 2)
        self.q_new, self.delta = q_update(self.q, self.alpha, self.reward, self.gamma, self.max_next)
        self.answer = self.q_new if self.task_type == "q_new" else self.delta
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Обновление Q-learning: δ = r + γ * max_next - Q, Q_new = Q + α * δ. "
                 "Ответ — целое или несократимая дробь.") if ru else
                ("Q-learning update: δ = r + γ * max_next - Q, Q_new = Q + α * δ. "
                 "Answer with an integer or a reduced fraction."))
        data = ((f"Q = {self.q}, α = {fmt_fraction(self.alpha)}, r = {self.reward}, "
                 f"γ = {fmt_fraction(self.gamma)}, max_next = {self.max_next}.") if ru else
                (f"Q = {self.q}, α = {fmt_fraction(self.alpha)}, r = {self.reward}, "
                 f"γ = {fmt_fraction(self.gamma)}, max_next = {self.max_next}."))
        ask = (("Найдите Q_new." if self.task_type == "q_new" else "Найдите δ.") if ru else
               ("Find Q_new." if self.task_type == "q_new" else "Find δ."))
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"δ = {fmt_fraction(self.delta)}, Q_new = {fmt_fraction(self.q_new)}.") if ru else
                (f"δ = {fmt_fraction(self.delta)}, Q_new = {fmt_fraction(self.q_new)}."))
        shown = fmt_fraction(self.answer)
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
