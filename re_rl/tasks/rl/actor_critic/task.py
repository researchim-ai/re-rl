"""ActorCriticTask — актор-критик на целых числах.

Критик ставит V(s) = r + V(s'). Актор сдвигает предпочтение действия на знак дельты.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Jump = Tuple[int, int, int, int]


def critic_trace(states: int, jumps: Sequence[Jump]) -> Tuple[List[Tuple[int, int, int, int]], List[int], List[List[int]]]:
    values = [0] * states
    prefs = [[0, 0] for _ in range(states)]
    trace = []
    for state, action, reward, nxt in jumps:
        delta = reward + values[nxt] - values[state]
        values[state] = reward + values[nxt]
        if delta > 0:
            prefs[state][action] += 1
        elif delta < 0:
            prefs[state][action] -= 1
        trace.append((delta, values[state], prefs[state][0], prefs[state][1]))
    return trace, values, prefs


def preferred_action(row: Sequence[int]) -> int:
    best = max(row)
    return min(index for index, value in enumerate(row) if value == best) + 1


class ActorCriticTask(BaseMathTask):
    TASK_TYPE = "actor_critic"
    TASK_TYPES = ["value", "action"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "s": 2, "m": 3}, 2: {"n": 3, "s": 2, "m": 3},
        3: {"n": 4, "s": 2, "m": 4}, 4: {"n": 5, "s": 3, "m": 4},
        5: {"n": 6, "s": 3, "m": 4}, 6: {"n": 7, "s": 3, "m": 5},
        7: {"n": 8, "s": 3, "m": 5}, 8: {"n": 9, "s": 4, "m": 5},
        9: {"n": 10, "s": 4, "m": 6}, 10: {"n": 12, "s": 4, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = max(2, int(p["s"]))
        limit = max(1, int(p["m"]))
        self.jumps = [
            (random.randrange(self.states), random.randrange(2),
             random.randint(-limit, limit), random.randrange(self.states))
            for _ in range(self.n)
        ]
        self.trace, self.values, self.prefs = critic_trace(self.states, self.jumps)
        self.k = random.randint(1, self.states)
        self.value = self.values[self.k - 1]
        self.action = preferred_action(self.prefs[self.k - 1])
        self.answer = self.value if self.task_type == "value" else self.action
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{state + 1}, {action + 1}, {reward}, {nxt + 1}"
            for state, action, reward, nxt in self.jumps
        )
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, states=self.states, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, ((state, action, reward, nxt), (delta, value, left, right)) in enumerate(
            zip(self.jumps, self.trace), 1,
        ):
            steps.append(texts.t(
                "s2", self.language, i=index, state=state + 1, action=action + 1,
                reward=reward, nxt=nxt + 1, delta=delta, value=value, left=left, right=right,
            ))
        steps.append(texts.t(
            "s3", self.language, k=self.k, value=self.value, action=self.action,
        ))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
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
