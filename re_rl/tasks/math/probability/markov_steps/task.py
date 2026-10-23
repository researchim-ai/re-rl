"""MarkovStepsTask — вес состояния после n шагов.

Из каждого состояния выходит две стрелки. Новый вес — сумма весов источников, умноженных на число стрелок.
Старт: состояние 1 имеет вес 1. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

ROWS = ((2, 0), (1, 1), (0, 2))


def markov_weights(rows: Sequence[Tuple[int, int]], steps: int) -> List[Tuple[int, int]]:
    weight = (1, 0)
    history = []
    for _ in range(steps):
        weight = (
            weight[0] * rows[0][0] + weight[1] * rows[1][0],
            weight[0] * rows[0][1] + weight[1] * rows[1][1],
        )
        history.append(weight)
    return history


class MarkovStepsTask(BaseMathTask):
    TASK_TYPE = "markov_steps"
    TASK_TYPES = ["state1", "state2"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.target = 0 if self.task_type == "state1" else 1
        self.rows = ((1, 1), (1, 1))
        self.history = markov_weights(self.rows, self.n)
        for _ in range(40):
            rows = (random.choice(ROWS), random.choice(ROWS))
            history = markov_weights(rows, self.n)
            if history[-1][self.target] != 0:
                self.rows = rows
                self.history = history
                break
        self.answer = self.history[-1][self.target]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "state1" else "s1"
        return texts.t(
            key, language, n=self.n,
            a0=self.rows[0][0], b0=self.rows[0][1],
            a1=self.rows[1][0], b1=self.rows[1][1],
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, w0=weight[0], w1=weight[1])
            for index, weight in enumerate(self.history, 1)
        ]
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
