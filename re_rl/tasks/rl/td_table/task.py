"""TdTableTask — табличный TD(0) с шагом 1 и gamma = 1.

Обновление V(s) = r + V(s'). Следующее значение уже учитывает прошлые записи.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Jump = Tuple[int, int, int]


def td_updates(states: int, jumps: Sequence[Jump]) -> List[List[int]]:
    values = [0] * states
    history = []
    for state, reward, nxt in jumps:
        values[state] = reward + values[nxt]
        history.append(list(values))
    return history


class TdTableTask(BaseMathTask):
    TASK_TYPE = "td_table"
    TASK_TYPES = ["value", "sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "s": 2, "m": 3}, 2: {"n": 2, "s": 2, "m": 3},
        3: {"n": 3, "s": 3, "m": 3}, 4: {"n": 3, "s": 3, "m": 4},
        5: {"n": 4, "s": 3, "m": 4}, 6: {"n": 5, "s": 3, "m": 4},
        7: {"n": 6, "s": 4, "m": 5}, 8: {"n": 7, "s": 4, "m": 5},
        9: {"n": 8, "s": 4, "m": 5}, 10: {"n": 10, "s": 4, "m": 6},
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
            (random.randrange(self.states), random.randint(-limit, limit), random.randrange(self.states))
            for _ in range(self.n)
        ]
        self.history = td_updates(self.states, self.jumps)
        self.values = self.history[-1]
        self.k = random.randint(1, self.states)
        self.value = self.values[self.k - 1]
        self.total = sum(self.values)
        self.answer = self.value if self.task_type == "value" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{index}: {state + 1}, {reward}, {nxt + 1}"
            for index, (state, reward, nxt) in enumerate(self.jumps, 1)
        )
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, states=self.states, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, ((state, reward, nxt), values) in enumerate(zip(self.jumps, self.history), 1):
            shown = ", ".join(str(value) for value in values)
            steps.append(texts.t(
                "s2", self.language, i=index, state=state + 1, reward=reward,
                nxt=nxt + 1, value=values[state], values=shown,
            ))
        steps.append(texts.t("s3", self.language, k=self.k, value=self.value, total=self.total))
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
