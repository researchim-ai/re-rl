"""PolicyEvalTask — синхронная оценка фиксированной политики.

Новая оценка состояния равна его награде плюс старая оценка следующего состояния.
Число проходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def eval_sweeps(rewards: Sequence[int], nxt: Sequence[int], sweeps: int) -> List[List[int]]:
    values = [0] * len(rewards)
    history = []
    for _ in range(sweeps):
        values = [rewards[state] + values[nxt[state]] for state in range(len(rewards))]
        history.append(list(values))
    return history


class PolicyEvalTask(BaseMathTask):
    TASK_TYPE = "policy_eval"
    TASK_TYPES = ["value", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "s": 2, "m": 2}, 2: {"n": 2, "s": 2, "m": 2},
        3: {"n": 3, "s": 2, "m": 2}, 4: {"n": 3, "s": 3, "m": 3},
        5: {"n": 4, "s": 3, "m": 3}, 6: {"n": 4, "s": 3, "m": 3},
        7: {"n": 5, "s": 3, "m": 3}, 8: {"n": 6, "s": 4, "m": 3},
        9: {"n": 7, "s": 4, "m": 3}, 10: {"n": 8, "s": 4, "m": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.states = max(2, int(p["s"]))
        limit = max(0, int(p["m"]))
        self.rewards = [random.randint(0, limit) for _ in range(self.states)]
        self.nxt = [random.randrange(self.states) for _ in range(self.states)]
        self.history = eval_sweeps(self.rewards, self.nxt, self.n)
        self.k = random.randint(1, self.states)
        self.value = self.history[-1][self.k - 1]
        self.total = sum(self.history[-1])
        self.answer = self.value if self.task_type == "value" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{index}: {reward}, {nxt + 1}"
            for index, (reward, nxt) in enumerate(zip(self.rewards, self.nxt), 1)
        )
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, states=self.states, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, values in enumerate(self.history, 1):
            shown = ", ".join(str(value) for value in values)
            steps.append(texts.t(
                "s2", self.language, i=index, row=shown, value=values[self.k - 1], total=sum(values),
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
