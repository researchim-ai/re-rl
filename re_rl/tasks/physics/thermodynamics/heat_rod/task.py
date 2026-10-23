"""HeatRodTask — явная схема теплопроводности на стержне.

Края закреплены. Внутренняя ячейка получает целую половину дискретного лапласиана.
Сетка считается массивом NumPy. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def heat_ticks(cells: Sequence[int], ticks: int) -> List[List[int]]:
    state = np.array(cells, dtype=np.int64)
    history = []
    for _ in range(ticks):
        nxt = state.copy()
        nxt[1:-1] = state[1:-1] + (state[:-2] - 2 * state[1:-1] + state[2:]) // 2
        state = nxt
        history.append([int(value) for value in state.tolist()])
    return history


class HeatRodTask(BaseMathTask):
    TASK_TYPE = "heat_rod"
    TASK_TYPES = ["cell", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "w": 3}, 2: {"n": 2, "w": 3}, 3: {"n": 3, "w": 3},
        4: {"n": 4, "w": 4}, 5: {"n": 5, "w": 4}, 6: {"n": 6, "w": 5},
        7: {"n": 7, "w": 5}, 8: {"n": 8, "w": 6}, 9: {"n": 9, "w": 6},
        10: {"n": 10, "w": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        interior = max(1, int(p["w"]))
        left = random.randint(0, 12)
        right = random.randint(0, 12)
        self.cells = [left] + [random.randint(0, 6) for _ in range(interior)] + [right]
        self.history = heat_ticks(self.cells, self.n)
        self.k = random.randint(2, len(self.cells) - 1)
        self.cell = self.history[-1][self.k - 1]
        self.total = sum(self.history[-1])
        self.answer = self.cell if self.task_type == "cell" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, row: Sequence[int]) -> str:
        return " ".join(str(value) for value in row)

    def _descr(self, language):
        key = "s0" if self.task_type == "cell" else "s1"
        return texts.t(key, language, listing=self._row(self.cells), n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, listing=self._row(row))
            for index, row in enumerate(self.history, 1)
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
