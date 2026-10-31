"""ExpectedSarsaTask — цель Expected SARSA при равномерной политике.

Среднее Q следующей позиции — сумма Q, делённая на число действий.
Цель равна r + γ * это среднее.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        shown = ", ".join(map(str, self.q_values))
        rule = ((texts.t('s0', language, n=self.n)))
        data = ((texts.t('s1', language, shown=shown, reward=self.reward, v2=fmt_fraction(self.gamma))))
        ask = (((texts.t('s3', language))) if self.task_type == "target" else
               ((texts.t('s4', language))))
        return f"{rule} {data} {ask}"

    def solve(self):
        from re_rl.tasks.rl.detailed_solvers import solve_detailed
        solve_detailed(self)

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
