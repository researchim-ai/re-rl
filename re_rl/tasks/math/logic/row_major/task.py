"""RowMajorTask — номер клетки в строке фиксированной ширины.

Номер строки — частное, номер столбца — остаток. Ширина равна числу номеров.
Число номеров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def index_trace(width: int, indices: Sequence[int]) -> List[Tuple[int, int, int]]:
    col_sum = 0
    trace = []
    for index in indices:
        row = index // width
        col = index % width
        col_sum += col
        trace.append((row, col, col_sum))
    return trace


class RowMajorTask(BaseMathTask):
    TASK_TYPE = "row_major"
    TASK_TYPES = ["row", "cols"]

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
        self.indices = [random.randint(0, self.n * self.n - 1) for _ in range(self.n)]
        self.trace = index_trace(self.n, self.indices)
        self.row = self.trace[-1][0]
        self.cols = self.trace[-1][2]
        self.answer = self.row if self.task_type == "row" else self.cols
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(index) for index in self.indices)
        key = "s0" if self.task_type == "row" else "s1"
        return texts.t(key, language, n=self.n, indices=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, item=item, row=row, col=col, cols=cols)
            for index, (item, (row, col, cols)) in enumerate(zip(self.indices, self.trace), 1)
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
