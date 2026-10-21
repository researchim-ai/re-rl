"""DoubleQTrajectoryTask — несколько обновлений Double Q-learning.

Две таблицы в начале нулевые. В записи указано, какая голова обновляется.
Действие для цели выбирает обновляемая голова: максимум, при равенстве меньший номер.
Значение этого действия берётся из другой головы. Номера с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Update = Tuple[int, int, int, int, int]


def apply_double_q(n_states: int, n_actions: int, updates: Sequence[Update],
                   alpha: Fraction, gamma: Fraction) -> List[List[List[Fraction]]]:
    tables = [[[Fraction(0) for _ in range(n_actions)] for _ in range(n_states)] for _ in range(2)]
    for state, action, reward, nxt, head in updates:
        other = 1 - head
        row = tables[head][nxt]
        best = max(row)
        chosen = min(index for index, value in enumerate(row) if value == best)
        target = reward + gamma * tables[other][nxt][chosen]
        current = tables[head][state][action]
        tables[head][state][action] = current + alpha * (target - current)
    return tables


class DoubleQTrajectoryTask(BaseMathTask):
    TASK_TYPE = "double_q_trajectory"
    TASK_TYPES = ["q_value", "best_action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 2, "u": 3, "mag": 3}, 2: {"s": 2, "u": 3, "mag": 4},
        3: {"s": 2, "u": 4, "mag": 4}, 4: {"s": 2, "u": 5, "mag": 5},
        5: {"s": 2, "u": 5, "mag": 5}, 6: {"s": 3, "u": 6, "mag": 6},
        7: {"s": 3, "u": 6, "mag": 6}, 8: {"s": 3, "u": 7, "mag": 7},
        9: {"s": 3, "u": 8, "mag": 8}, 10: {"s": 3, "u": 8, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_states = int(p["s"])
        self.n_updates = int(p["u"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n_actions = 2
        self.alpha = Fraction(1, 2) if difficulty >= 6 and random.random() < 0.5 else Fraction(1, 1)
        self.gamma = Fraction(1, 2) if difficulty >= 4 and random.random() < 0.7 else Fraction(1, 1)
        self.updates = [
            (random.randrange(self.n_states), random.randrange(self.n_actions),
             random.randint(0, self.mag), random.randrange(self.n_states),
             random.randrange(2))
            for _ in range(self.n_updates)
        ]
        self.tables = apply_double_q(self.n_states, self.n_actions, self.updates, self.alpha, self.gamma)
        self.head = random.randrange(2)
        self.state = random.randrange(self.n_states)
        self.action = random.randrange(self.n_actions)
        row = self.tables[self.head][self.state]
        best = max(row)
        self.best = min(index for index, value in enumerate(row) if value == best) + 1
        self.answer = row[self.action] if self.task_type == "q_value" else Fraction(self.best)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return "; ".join(
            f"{head + 1}, {state + 1}, {action + 1}, {reward}, {nxt + 1}"
            for state, action, reward, nxt, head in self.updates
        )

    def _descr(self, language):
        rule = ((texts.t('s0', language, n_states=self.n_states, v1=fmt_fraction(self.alpha), v2=fmt_fraction(self.gamma), v3=self._shown())))
        if self.task_type == "q_value":
            ask = ((texts.t('s2', language, v0=self.head + 1, v1=self.state + 1, v2=self.action + 1)))
        else:
            ask = ((texts.t('s3', language, v0=self.head + 1, v1=self.state + 1)))
        return f"{rule} {ask}"

    def solve(self):
        value = self.tables[self.head][self.state][self.action]
        shown = str(self.best) if self.task_type == "best_action" else fmt_fraction(value)
        step = ((texts.t('s1', self.language, v0=self.head + 1, v1=self.state + 1, v2=self.action + 1, v3=fmt_fraction(value), best=self.best)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "best_action":
            return U.verify_int(prediction, self.best)
        return verify_fraction(prediction, self.tables[self.head][self.state][self.action])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
