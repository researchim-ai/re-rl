"""CellWriteTask — последняя запись в клетку массива.

Клетки начинают с нуля. Новая запись в ту же клетку затирает старое значение.
Число записей равно длине массива и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Write = Tuple[int, int]


def write_trace(size: int, writes: Sequence[Write], query: int) -> List[Tuple[int, int]]:
    cells = [0] * size
    trace = []
    for index, value in writes:
        if 0 <= index < size:
            cells[index] = value
        trace.append((cells[query], sum(cells)))
    return trace


class CellWriteTask(BaseMathTask):
    TASK_TYPE = "cell_write"
    TASK_TYPES = ["cell", "total"]

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
        self.writes = [(random.randint(0, self.n - 1), random.randint(0, 6)) for _ in range(self.n)]
        self.query = random.randint(0, self.n - 1)
        self.trace = write_trace(self.n, self.writes, self.query)
        self.cell = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.cell if self.task_type == "cell" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{index} {value}" for index, value in self.writes)
        key = "s0" if self.task_type == "cell" else "s1"
        return texts.t(key, language, n=self.n, query=self.query, writes=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, place=place, value=value, cell=cell, total=total)
            for index, ((place, value), (cell, total)) in enumerate(zip(self.writes, self.trace), 1)
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
