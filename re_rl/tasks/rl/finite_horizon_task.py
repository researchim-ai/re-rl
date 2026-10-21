"""FiniteHorizonTask — обратная индукция в конечном горизонте.

Детерминированный МДП. После последнего шага оценка равна 0.
На каждом шаге V = max (награда + γ * V следующего состояния).
При равенстве выбирается действие с меньшим номером. Номера с 1.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def finite_horizon(rewards: Sequence[Sequence[int]], nexts: Sequence[Sequence[int]],
                   horizon: int, gamma: Fraction) -> Tuple[List[Fraction], List[int]]:
    n_states = len(rewards)
    n_actions = len(rewards[0])
    values = [Fraction(0) for _ in range(n_states)]
    actions = [1 for _ in range(n_states)]
    for _ in range(horizon):
        new_values: List[Fraction] = []
        new_actions: List[int] = []
        for state in range(n_states):
            best_value = None
            best_action = 0
            for action in range(n_actions):
                candidate = rewards[state][action] + gamma * values[nexts[state][action]]
                if best_value is None or candidate > best_value:
                    best_value = candidate
                    best_action = action
            new_values.append(best_value)
            new_actions.append(best_action + 1)
        values = new_values
        actions = new_actions
    return values, actions


class FiniteHorizonTask(BaseMathTask):
    TASK_TYPE = "finite_horizon"
    TASK_TYPES = ["value", "action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 2, "h": 2, "mag": 3}, 2: {"s": 2, "h": 3, "mag": 4},
        3: {"s": 3, "h": 3, "mag": 4}, 4: {"s": 3, "h": 4, "mag": 5},
        5: {"s": 3, "h": 4, "mag": 5}, 6: {"s": 3, "h": 5, "mag": 6},
        7: {"s": 4, "h": 5, "mag": 6}, 8: {"s": 4, "h": 5, "mag": 7},
        9: {"s": 4, "h": 6, "mag": 8}, 10: {"s": 4, "h": 6, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_states = int(p["s"])
        self.horizon = int(p["h"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n_actions = 2
        self.gamma = Fraction(1, 2) if difficulty >= 5 and random.random() < 0.6 else Fraction(1, 1)
        self.rewards = [
            [random.randint(-self.mag, self.mag) for _ in range(self.n_actions)]
            for _ in range(self.n_states)
        ]
        self.nexts = [
            [random.randrange(self.n_states) for _ in range(self.n_actions)]
            for _ in range(self.n_states)
        ]
        self.values, self.actions = finite_horizon(self.rewards, self.nexts, self.horizon, self.gamma)
        self.state = random.randrange(self.n_states)
        self.answer = self.values[self.state] if self.task_type == "value" else Fraction(self.actions[self.state])
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rules(self) -> str:
        parts = []
        for state in range(self.n_states):
            for action in range(self.n_actions):
                parts.append(
                    f"{state + 1}, {action + 1}: r={self.rewards[state][action]}, "
                    f"next={self.nexts[state][action] + 1}"
                )
        return "; ".join(parts)

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"Детерминированный процесс, горизонт {self.horizon}, γ = {fmt_fraction(self.gamma)}. "
                 f"Состояния и действия нумеруются с 1, действий два. После последнего шага оценка равна 0. "
                 f"На каждом шаге берётся награда + γ * оценка следующего состояния; при равенстве — меньшее действие. "
                 f"Переходы: {self._rules()}. Ответ — целое или несократимая дробь.") if ru else
                (f"Deterministic process, horizon {self.horizon}, γ = {fmt_fraction(self.gamma)}. "
                 f"States and actions start at 1, and there are two actions. The value after the last step is 0. "
                 f"Each step takes reward + γ * value of the next state; ties take the smaller action. "
                 f"Transitions: {self._rules()}. Answer with an integer or a reduced fraction."))
        if self.task_type == "value":
            ask = ((f"Найдите оценку состояния {self.state + 1} перед первым шагом.") if ru else
                   (f"Find the value of state {self.state + 1} before the first step."))
        else:
            ask = ((f"Какое действие выбирается в состоянии {self.state + 1} перед первым шагом?") if ru else
                   (f"Which action is chosen in state {self.state + 1} before the first step?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = str(self.actions[self.state]) if self.task_type == "action" else fmt_fraction(self.values[self.state])
        step = ((f"Оценка состояния {self.state + 1} равна {fmt_fraction(self.values[self.state])}, "
                 f"действие {self.actions[self.state]}.") if ru else
                (f"Value of state {self.state + 1} is {fmt_fraction(self.values[self.state])}, "
                 f"action {self.actions[self.state]}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "action":
            return U.verify_int(prediction, self.actions[self.state])
        return verify_fraction(prediction, self.values[self.state])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
