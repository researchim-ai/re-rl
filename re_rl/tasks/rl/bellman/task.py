"""BellmanBackupTask — один шаг оптимальности Беллмана.

Два действия. Q(a) = r(a) + γ * V(следующего состояния).
Оптимальная оценка — максимум, жадное действие — то, у кого Q больше.
При равенстве выборка пересобирается.

Подтипы: ``value`` и ``greedy``.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class BellmanBackupTask(BaseMathTask):
    TASK_TYPE = "bellman_backup"
    TASK_TYPES = ["value", "greedy"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mag": 4}, 2: {"mag": 5}, 3: {"mag": 6}, 4: {"mag": 6}, 5: {"mag": 8},
        6: {"mag": 8}, 7: {"mag": 10}, 8: {"mag": 10}, 9: {"mag": 12}, 10: {"mag": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.gamma = Fraction(1, 2) if random.random() < 0.6 else Fraction(1, 1)
        for _ in range(30):
            self.r_a = random.randint(0, self.mag)
            self.r_b = random.randint(0, self.mag)
            self.v_a = random.randint(0, self.mag)
            self.v_b = random.randint(0, self.mag)
            self.q_a = self.r_a + self.gamma * self.v_a
            self.q_b = self.r_b + self.gamma * self.v_b
            if self.q_a != self.q_b:
                break
        else:
            self.r_a += 1
            self.q_a = self.r_a + self.gamma * self.v_a
        self.greedy = "A" if self.q_a > self.q_b else "B"
        self.value = max(self.q_a, self.q_b)

    def _descr(self, language):
        gamma = fmt_fraction(self.gamma)
        rule = ((texts.t('s0', language, gamma=gamma)))
        data = ((texts.t('s1', language, r_a=self.r_a, v_a=self.v_a, r_b=self.r_b, v_b=self.v_b)))
        if self.task_type == "value":
            ask = ((texts.t('s2', language)))
        else:
            ask = ((texts.t('s3', language)))
        return f"{rule} {data} {ask}"

    def solve(self):
        from re_rl.tasks.rl.detailed_solvers import solve_detailed
        solve_detailed(self)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "greedy":
            return U.verify_label(prediction, [self.greedy])
        return verify_fraction(prediction, self.value)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
