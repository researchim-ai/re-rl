"""TraceDecayTask — след, который на каждом визите делится пополам.

Сначала каждая координата делится на 2 с округлением вниз, затем к посещённой прибавляется 1.
Число визитов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def decay_visits(states: int, visits: Sequence[int]) -> List[List[int]]:
    values = [0] * states
    history = []
    for visit in visits:
        values = [value // 2 for value in values]
        values[visit] += 1
        history.append(list(values))
    return history


class TraceDecayTask(BaseMathTask):
    TASK_TYPE = "trace_decay"
    TASK_TYPES = ["cell", "mass"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "s": 3}, 2: {"n": 2, "s": 3}, 3: {"n": 3, "s": 3},
        4: {"n": 3, "s": 3}, 5: {"n": 4, "s": 3}, 6: {"n": 5, "s": 4},
        7: {"n": 6, "s": 4}, 8: {"n": 7, "s": 4}, 9: {"n": 8, "s": 4},
        10: {"n": 10, "s": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = max(2, int(p["s"]))
        self.visits = [random.randrange(self.states) for _ in range(self.n)]
        self.history = decay_visits(self.states, self.visits)
        self.values = self.history[-1]
        self.k = random.randint(1, self.states)
        self.cell = self.values[self.k - 1]
        self.mass = sum(self.values)
        self.answer = self.cell if self.task_type == "cell" else self.mass
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(visit + 1) for visit in self.visits)
        key = "s0" if self.task_type == "cell" else "s1"
        return texts.t(key, language, states=self.states, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, (visit, values) in enumerate(zip(self.visits, self.history), 1):
            shown = ", ".join(str(value) for value in values)
            steps.append(texts.t("s2", self.language, i=index, visit=visit + 1, values=shown))
        steps.append(texts.t("s3", self.language, k=self.k, cell=self.cell, mass=self.mass))
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
