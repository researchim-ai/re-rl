"""EpsilonGreedyTask — выбор действия по ε-жадной схеме с одним случайным числом.

Если u >= ε, берётся действие с максимальным Q; при равенстве — меньший номер.
Если u < ε, номер с нуля равен целой части (u/ε)*n.
Номера действий в ответе с 1. u всегда меньше 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def epsilon_choice(q_values: List[int], epsilon: Fraction, draw: Fraction) -> int:
    """Возвращает номер действия с 1."""
    n = len(q_values)
    if epsilon == 0 or draw >= epsilon:
        best = max(q_values)
        return min(i for i, value in enumerate(q_values) if value == best) + 1
    index = int(draw / epsilon * n)
    if index >= n:
        index = n - 1
    if index < 0:
        index = 0
    return index + 1


class EpsilonGreedyTask(BaseMathTask):
    TASK_TYPE = "epsilon_greedy"
    TASK_TYPES = ["action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 5}, 2: {"n": 2, "mag": 6}, 3: {"n": 3, "mag": 6},
        4: {"n": 3, "mag": 8}, 5: {"n": 4, "mag": 8}, 6: {"n": 4, "mag": 10},
        7: {"n": 5, "mag": 10}, 8: {"n": 5, "mag": 12}, 9: {"n": 6, "mag": 12},
        10: {"n": 6, "mag": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "action"
        self.augment = augment
        self.q_values = [random.randint(0, self.mag) for _ in range(self.n)]
        if random.random() < 0.4:
            top = max(self.q_values)
            self.q_values[random.randrange(self.n)] = top
        options = [Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1)]
        self.epsilon = random.choice(options[:2 + min(3, difficulty // 2)])
        self.draw = Fraction(random.randrange(12), 12)
        self.answer = epsilon_choice(self.q_values, self.epsilon, self.draw)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        qs = ", ".join(f"{i + 1}: {q}" for i, q in enumerate(self.q_values))
        rule = ((texts.t('s0', language)))
        data = ((texts.t('s1', language, qs=qs, epsilon=self.epsilon, draw=self.draw)))
        ask = ((texts.t('s2', language)))
        return f"{rule} {data} {ask}"

    def solve(self):
        mode = (texts.t('s4', self.language) if self.draw >= self.epsilon or self.epsilon == 0 else texts.t('s5', self.language))
        mode_en = ("greedy" if self.draw >= self.epsilon or self.epsilon == 0 else "explore")
        step = ((texts.t('s3', self.language, mode=mode, answer=self.answer)))
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
