"""TargetSyncTask — онлайн-оценка и редкое копирование в целевую таблицу.

Онлайн читает целевую таблицу. Копия делается в конце каждого кратного шага.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Jump = Tuple[int, int, int]


def sync_trace(states: int, jumps: Sequence[Jump], period: int) -> List[Tuple[int, int, int, List[int], List[int]]]:
    online = [0] * states
    target = [0] * states
    trace = []
    for index, (state, reward, nxt) in enumerate(jumps, 1):
        online[state] = reward + target[nxt]
        copied = 0
        if index % period == 0:
            target = list(online)
            copied = 1
        trace.append((online[state], copied, list(online), list(target)))
    return trace


class TargetSyncTask(BaseMathTask):
    TASK_TYPE = "target_sync"
    TASK_TYPES = ["online", "target"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "s": 2, "p": 2, "m": 3}, 2: {"n": 4, "s": 2, "p": 2, "m": 3},
        3: {"n": 5, "s": 2, "p": 2, "m": 4}, 4: {"n": 6, "s": 3, "p": 3, "m": 4},
        5: {"n": 7, "s": 3, "p": 3, "m": 4}, 6: {"n": 8, "s": 3, "p": 3, "m": 5},
        7: {"n": 9, "s": 3, "p": 4, "m": 5}, 8: {"n": 10, "s": 4, "p": 4, "m": 5},
        9: {"n": 12, "s": 4, "p": 4, "m": 6}, 10: {"n": 14, "s": 4, "p": 4, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = max(2, int(p["s"]))
        self.period = max(1, int(p["p"]))
        limit = max(1, int(p["m"]))
        self.jumps = [
            (random.randrange(self.states), random.randint(-limit, limit), random.randrange(self.states))
            for _ in range(self.n)
        ]
        self.trace = sync_trace(self.states, self.jumps, self.period)
        _, _, self.online, self.target = self.trace[-1]
        self.k = random.randint(1, self.states)
        self.online_value = self.online[self.k - 1]
        self.target_value = self.target[self.k - 1]
        self.answer = self.online_value if self.task_type == "online" else self.target_value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{state + 1}, {reward}, {nxt + 1}" for state, reward, nxt in self.jumps
        )
        key = "s0" if self.task_type == "online" else "s1"
        return texts.t(
            key, language, states=self.states, n=self.n, period=self.period,
            listing=listing, k=self.k,
        )

    def solve(self):
        steps = []
        for index, ((state, reward, nxt), (value, copied, online, target)) in enumerate(
            zip(self.jumps, self.trace), 1,
        ):
            steps.append(texts.t(
                "s2", self.language, i=index, state=state + 1, reward=reward, nxt=nxt + 1,
                value=value, copied=copied, k=self.k,
                online=online[self.k - 1], target=target[self.k - 1],
            ))
        steps.append(texts.t(
            "s3", self.language, k=self.k, online=self.online_value, target=self.target_value,
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
