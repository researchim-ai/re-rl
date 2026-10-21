"""DoubleQTask — цель Double Q-learning.

Действие выбирает первая голова: argmax Q1, при равенстве меньший номер.
Цель равна r + γ * Q2 этого действия. Номера действий с 1.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def double_q_target(q1: List[int], q2: List[int], reward: int, gamma: Fraction) -> Tuple[int, Fraction]:
    best = max(q1)
    index = min(i for i, value in enumerate(q1) if value == best)
    return index + 1, reward + gamma * q2[index]


class DoubleQTask(BaseMathTask):
    TASK_TYPE = "double_q"
    TASK_TYPES = ["action", "target"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 4}, 2: {"n": 2, "mag": 5}, 3: {"n": 3, "mag": 5},
        4: {"n": 3, "mag": 6}, 5: {"n": 3, "mag": 8}, 6: {"n": 4, "mag": 8},
        7: {"n": 4, "mag": 10}, 8: {"n": 5, "mag": 10}, 9: {"n": 5, "mag": 12},
        10: {"n": 6, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.q1 = [random.randint(0, self.mag) for _ in range(self.n)]
        self.q2 = [random.randint(0, self.mag) for _ in range(self.n)]
        if random.random() < 0.35:
            top = max(self.q1)
            self.q1[random.randrange(self.n)] = top
        self.reward = random.randint(0, self.mag)
        self.gamma = Fraction(1, 2) if difficulty >= 4 and random.random() < 0.7 else Fraction(1, 1)
        self.action, self.target = double_q_target(self.q1, self.q2, self.reward, self.gamma)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pairs(self) -> str:
        return ", ".join(f"{i + 1}: Q1={a}, Q2={b}" for i, (a, b) in enumerate(zip(self.q1, self.q2)))

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Double Q-learning. Действие выбирает Q1: максимум, при равенстве меньший номер. "
                 "Цель = r + γ * Q2(выбранного действия).") if ru else
                ("Double Q-learning. Q1 selects the action: the maximum, ties go to the smaller index. "
                 "The target is r + γ * Q2(selected action)."))
        data = ((f"Действия: {self._pairs()}. r = {self.reward}, γ = {fmt_fraction(self.gamma)}.") if ru else
                (f"Actions: {self._pairs()}. r = {self.reward}, γ = {fmt_fraction(self.gamma)}."))
        if self.task_type == "action":
            ask = ("Какое действие выбрано? Ответьте номером." if ru else
                   "Which action is selected? Answer with its index.")
        else:
            ask = ("Найдите цель. Ответ — целое или несократимая дробь." if ru else
                   "Find the target. Answer with an integer or a reduced fraction.")
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = str(self.action) if self.task_type == "action" else fmt_fraction(self.target)
        step = ((f"Действие {self.action}, цель {fmt_fraction(self.target)}.") if ru else
                (f"Action {self.action}, target {fmt_fraction(self.target)}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "action":
            return U.verify_int(prediction, self.action)
        return verify_fraction(prediction, self.target)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
