"""UpwindRowTask — перенос значений на одну клетку вправо.

Правая клетка покидает ряд, левая становится нулём. Сдвиг делает NumPy.
Число тактов равно длине ряда и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def wind_trace(cells: Sequence[int], ticks: int) -> List[Tuple[int, int]]:
    state = np.asarray(cells, dtype=np.int64)
    lost = 0
    trace = []
    for _ in range(ticks):
        lost += int(state[-1])
        state = np.roll(state, 1)
        state[0] = 0
        trace.append((int(state.sum()), lost))
    return trace


class UpwindRowTask(BaseMathTask):
    TASK_TYPE = "upwind_row"
    TASK_TYPES = ["kept", "lost"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.cells = [random.randint(0, 5) for _ in range(self.n)]
        self.trace = wind_trace(self.cells, self.n)
        self.kept = self.trace[-1][0]
        self.lost = self.trace[-1][1]
        self.answer = self.kept if self.task_type == "kept" else self.lost
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(cell) for cell in self.cells)
        key = "s0" if self.task_type == "kept" else "s1"
        return texts.t(key, language, n=self.n, cells=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kept=kept, lost=lost)
            for index, (kept, lost) in enumerate(self.trace, 1)
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
