"""ExpectedSarsaTask — цель Expected SARSA при равномерной политике.

Среднее Q следующей позиции — сумма Q, делённая на число действий.
Цель равна r + γ * это среднее.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def uniform_backup(q_values: List[int], reward: int, gamma: Fraction) -> Tuple[Fraction, Fraction]:
    mean = Fraction(sum(q_values), len(q_values))
    return mean, reward + gamma * mean


class ExpectedSarsaTask(BaseMathTask):
    TASK_TYPE = "expected_sarsa"
    TASK_TYPES = ["target", "mean"]

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
        self.q_values = [random.randint(0, self.mag) for _ in range(self.n)]
        self.reward = random.randint(0, self.mag)
        self.gamma = Fraction(1, 2) if difficulty >= 4 and random.random() < 0.7 else Fraction(1, 1)
        self.mean, self.target = uniform_backup(self.q_values, self.reward, self.gamma)
        self.answer = self.target if self.task_type == "target" else self.mean
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(map(str, self.q_values))
        rule = ((f"Expected SARSA. Политика на следующем шаге равномерная: "
                 f"каждое действие имеет вероятность 1/{self.n}. "
                 f"Среднее Q — сумма оценок, делённая на число действий. "
                 f"Цель = r + γ * среднее. Ответ — целое или несократимая дробь.") if ru else
                (f"Expected SARSA. The next-step policy is uniform: "
                 f"each action has probability 1/{self.n}. "
                 f"The mean Q is the sum of the values divided by the number of actions. "
                 f"The target is r + γ * mean. Answer with an integer or a reduced fraction."))
        data = ((f"Q следующего состояния: {shown}. r = {self.reward}, γ = {fmt_fraction(self.gamma)}.")
                if ru else
                (f"Next-state Q: {shown}. r = {self.reward}, γ = {fmt_fraction(self.gamma)}."))
        ask = (("Найдите цель." if ru else "Find the target.") if self.task_type == "target" else
               ("Найдите среднее Q." if ru else "Find the mean Q."))
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Среднее {fmt_fraction(self.mean)}, цель {fmt_fraction(self.target)}.") if ru else
                (f"Mean {fmt_fraction(self.mean)}, target {fmt_fraction(self.target)}."))
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
