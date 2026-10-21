"""DoubleQTrajectoryTask — несколько обновлений Double Q-learning.

Две таблицы в начале нулевые. В записи указано, какая голова обновляется.
Действие для цели выбирает обновляемая голова: максимум, при равенстве меньший номер.
Значение этого действия берётся из другой головы. Номера с 1.
"""

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
        ru = language == "ru"
        rule = ((f"Double Q-learning, обе таблицы в начале нулевые. Состояний {self.n_states}, действий 2. "
                 f"α = {fmt_fraction(self.alpha)}, γ = {fmt_fraction(self.gamma)}. "
                 f"Запись: голова, состояние, действие, награда, следующее состояние. {self._shown()}. "
                 f"Действие для цели выбирает обновляемая голова: максимум в следующем состоянии, "
                 f"при равенстве меньший номер. Значение берётся из другой головы. "
                 f"Лучшее действие головы — её собственный максимум, при равенстве меньший номер. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"Double Q-learning, both tables start at zero. There are {self.n_states} states and 2 actions. "
                 f"α = {fmt_fraction(self.alpha)}, γ = {fmt_fraction(self.gamma)}. "
                 f"A record is head, state, action, reward, next state. {self._shown()}. "
                 f"The updated head selects the target action: the maximum in the next state, "
                 f"ties take the smaller index. The value comes from the other head. "
                 f"A head's best action is its own maximum, ties take the smaller index. "
                 f"Answer with an integer or a reduced fraction."))
        if self.task_type == "q_value":
            ask = ((f"Найдите Q головы {self.head + 1} для состояния {self.state + 1} и действия {self.action + 1}.")
                   if ru else
                   (f"Find head {self.head + 1}'s Q for state {self.state + 1} and action {self.action + 1}."))
        else:
            ask = ((f"Какое действие лучше у головы {self.head + 1} в состоянии {self.state + 1}?") if ru else
                   (f"Which action is best for head {self.head + 1} in state {self.state + 1}?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        value = self.tables[self.head][self.state][self.action]
        shown = str(self.best) if self.task_type == "best_action" else fmt_fraction(value)
        step = ((f"Q головы {self.head + 1} для ({self.state + 1}, {self.action + 1}) равно {fmt_fraction(value)}, "
                 f"лучшее действие {self.best}.") if ru else
                (f"Head {self.head + 1} Q for ({self.state + 1}, {self.action + 1}) is {fmt_fraction(value)}, "
                 f"best action {self.best}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
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
