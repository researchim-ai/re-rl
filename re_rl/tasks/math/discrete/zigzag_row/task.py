"""ZigzagRowTask — треугольник Энтрингера.

E(1, 1) = 1. Дальше E(t, k) = E(t, k-1) + E(t-1, t-k), а недостающее слагаемое равно 0.
Последнее число строки t — число знакопеременных перестановок. Номер строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def entringer_rows(limit: int) -> List[List[int]]:
    rows = [[0, 1]]
    for size in range(2, limit + 1):
        previous = rows[-1]
        row = [0]
        for k in range(1, size + 1):
            index = size - k
            earlier = 0 if index == 0 else previous[index]
            row.append(row[-1] + earlier)
        rows.append(row)
    return rows


class ZigzagRowTask(BaseMathTask):
    TASK_TYPE = "zigzag_row"
    TASK_TYPES = ["corner", "entry"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rows = entringer_rows(self.n)
        self.k = random.randint(1, self.n)
        self.corner = self.rows[-1][-1]
        self.entry = self.rows[-1][self.k]
        self.answer = self.corner if self.task_type == "corner" else self.entry
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "corner":
            return texts.t("s0", language, n=self.n)
        return texts.t("s1", language, n=self.n, k=self.k)

    def solve(self):
        steps = []
        for index, row in enumerate(self.rows, 1):
            listing = " ".join(str(value) for value in row[1:])
            steps.append(texts.t("s2", self.language, i=index, listing=listing))
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
