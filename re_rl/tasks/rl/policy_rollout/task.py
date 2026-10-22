"""PolicyRolloutTask — сумма наград при заданной политике на отрезке.

Это не оптимальная ценность, а прогон указанных действий. У края действие наружу оставляет агента на месте.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class PolicyRolloutTask(BaseMathTask):
    TASK_TYPE = "policy_rollout"
    TASK_TYPES = ["reward", "end"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "s": 3, "m": 3}, 2: {"n": 3, "s": 3, "m": 3},
        3: {"n": 4, "s": 4, "m": 4}, 4: {"n": 4, "s": 4, "m": 4},
        5: {"n": 5, "s": 5, "m": 5}, 6: {"n": 6, "s": 5, "m": 5},
        7: {"n": 7, "s": 6, "m": 6}, 8: {"n": 8, "s": 6, "m": 6},
        9: {"n": 9, "s": 7, "m": 7}, 10: {"n": 10, "s": 8, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.length = max(2, int(p["s"]))
        mag = int(p["m"])
        self.policy = [random.choice((-1, 1)) for _ in range(self.length)]
        self.rewards = [random.randint(-mag, mag) for _ in range(self.length)]
        self.start = random.randrange(self.length)
        position = self.start
        self.total = 0
        self.trace: List[Tuple[int, int, int, int]] = []
        for _ in range(self.n):
            action = self.policy[position]
            nxt = min(self.length - 1, max(0, position + action))
            self.total += self.rewards[nxt]
            self.trace.append((position, action, nxt, self.total))
            position = nxt
        self.end = position
        self.answer = self.total if self.task_type == "reward" else self.end
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        policy = ", ".join(f"{index}:{action:+d}" for index, action in enumerate(self.policy))
        rewards = ", ".join(str(item) for item in self.rewards)
        key = "s0" if self.task_type == "reward" else "s1"
        return texts.t(
            key, language, n=self.n, last=self.length - 1, start=self.start,
            policy=policy, rewards=rewards,
        )

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=i, pos=pos, action=f"{action:+d}",
                nxt=nxt, gain=self.rewards[nxt], total=total,
            )
            for i, (pos, action, nxt, total) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, reward=self.total, end=self.end))
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
