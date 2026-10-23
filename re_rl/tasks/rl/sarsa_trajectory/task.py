"""SarsaTrajectoryTask — несколько обновлений SARSA подряд.

В цели стоит Q именно выбранного следующего действия, а не максимум.
Таблица в начале нулевая. Номера состояний и действий с 1.
Лучшее действие при равенстве — меньший номер.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction
from re_rl.tasks.rl.q_trajectory_task import greedy_action

Update = Tuple[int, int, int, int, int]


def apply_sarsa(n_states: int, n_actions: int, updates: Sequence[Update],
                alpha: Fraction, gamma: Fraction) -> List[List[Fraction]]:
    table = [[Fraction(0) for _ in range(n_actions)] for _ in range(n_states)]
    for state, action, reward, nxt, next_action in updates:
        target = reward + gamma * table[nxt][next_action]
        delta = target - table[state][action]
        table[state][action] = table[state][action] + alpha * delta
    return table


class SarsaTrajectoryTask(BaseMathTask):
    TASK_TYPE = "sarsa_trajectory"
    TASK_TYPES = ["q_value", "best_action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 2, "u": 3, "mag": 3}, 2: {"s": 2, "u": 4, "mag": 4},
        3: {"s": 2, "u": 4, "mag": 4}, 4: {"s": 2, "u": 5, "mag": 5},
        5: {"s": 3, "u": 5, "mag": 5}, 6: {"s": 3, "u": 6, "mag": 6},
        7: {"s": 3, "u": 7, "mag": 6}, 8: {"s": 3, "u": 8, "mag": 7},
        9: {"s": 3, "u": 9, "mag": 8}, 10: {"s": 3, "u": 10, "mag": 8},
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
             random.randrange(self.n_actions))
            for _ in range(self.n_updates)
        ]
        self.table = apply_sarsa(self.n_states, self.n_actions, self.updates, self.alpha, self.gamma)
        self.state = random.randrange(self.n_states)
        self.action = random.randrange(self.n_actions)
        self.best = greedy_action(self.table[self.state])
        self.answer = (self.table[self.state][self.action] if self.task_type == "q_value"
                       else Fraction(self.best))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return "; ".join(
            f"{state + 1}, {action + 1}, {reward}, {nxt + 1}, {next_action + 1}"
            for state, action, reward, nxt, next_action in self.updates
        )

    def _descr(self, language):
        rule = ((texts.t('s0', language, n_states=self.n_states, v1=fmt_fraction(self.alpha), v2=fmt_fraction(self.gamma), v3=self._shown())))
        if self.task_type == "q_value":
            ask = ((texts.t('s2', language, v0=self.state + 1, v1=self.action + 1)))
        else:
            ask = ((texts.t('s3', language, v0=self.state + 1)))
        return f"{rule} {ask}"

    def solve(self):
        table = [[Fraction(0) for _ in range(self.n_actions)] for _ in range(self.n_states)]
        steps = []
        for index, (state, action, reward, nxt, next_action) in enumerate(self.updates, 1):
            target = table[nxt][next_action]
            updated = table[state][action] + self.alpha * (reward + self.gamma * target - table[state][action])
            table[state][action] = updated
            row = ", ".join(fmt_fraction(value) for value in table[state])
            steps.append(texts.t(
                "s4", self.language, i=index, state=state + 1, action=action + 1,
                reward=reward, nxt=nxt + 1, next_action=next_action + 1,
                target=fmt_fraction(target), q=fmt_fraction(updated), row=row,
            ))
        shown = (str(self.best) if self.task_type == "best_action"
                 else fmt_fraction(self.table[self.state][self.action]))
        steps.append(texts.t(
            "s1", self.language, v0=self.state + 1, v1=self.action + 1,
            v2=fmt_fraction(self.table[self.state][self.action]), best=self.best,
        ))
        steps.append(texts.common("answer_line", self.language, answer=shown))
        self.solution_steps = steps
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "best_action":
            return U.verify_int(prediction, self.best)
        return verify_fraction(prediction, self.table[self.state][self.action])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
