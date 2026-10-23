"""FiniteHorizonTask — обратная индукция в конечном горизонте.

Детерминированный МДП. После последнего шага оценка равна 0.
На каждом шаге V = max (награда + γ * V следующего состояния).
При равенстве выбирается действие с меньшим номером. Номера с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        rule = ((texts.t('s0', language, horizon=self.horizon, v1=fmt_fraction(self.gamma), v2=self._rules())))
        if self.task_type == "value":
            ask = ((texts.t('s2', language, v0=self.state + 1)))
        else:
            ask = ((texts.t('s3', language, v0=self.state + 1)))
        return f"{rule} {ask}"

    def solve(self):
        values = [Fraction(0) for _ in range(self.n_states)]
        actions = [1 for _ in range(self.n_states)]
        steps = []
        for index in range(1, self.horizon + 1):
            new_values = []
            new_actions = []
            for state in range(self.n_states):
                best_value = None
                best_action = 0
                for action in range(self.n_actions):
                    candidate = self.rewards[state][action] + self.gamma * values[self.nexts[state][action]]
                    if best_value is None or candidate > best_value:
                        best_value = candidate
                        best_action = action
                new_values.append(best_value)
                new_actions.append(best_action + 1)
            values = new_values
            actions = new_actions
            row = "; ".join(
                f"{state + 1}: {fmt_fraction(values[state])}/{actions[state]}"
                for state in range(self.n_states)
            )
            steps.append(texts.t("s4", self.language, i=index, row=row))
        shown = str(self.actions[self.state]) if self.task_type == "action" else fmt_fraction(self.values[self.state])
        steps.append(texts.t(
            "s1", self.language, v0=self.state + 1,
            v1=fmt_fraction(self.values[self.state]), v2=self.actions[self.state],
        ))
        steps.append(texts.common("answer_line", self.language, answer=shown))
        self.solution_steps = steps
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
