"""PascalRowTask — элемент строки треугольника Паскаля.

Строка 0 равна 1. Каждая следующая получается сложением соседей, по краям единицы.
Номер строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pascal_rows(row: int) -> List[List[int]]:
    rows = [[1]]
    for _ in range(row):
        previous = rows[-1]
        nxt = [1]
        for index in range(len(previous) - 1):
            nxt.append(previous[index] + previous[index + 1])
        nxt.append(1)
        rows.append(nxt)
    return rows


class PascalRowTask(BaseMathTask):
    TASK_TYPE = "pascal_row"
    TASK_TYPES = ["entry", "middle"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.rows = pascal_rows(self.n)
        self.k = random.randint(1, self.n + 1)
        self.entry = self.rows[self.n][self.k - 1]
        self.middle_index = self.n // 2
        self.middle = self.rows[self.n][self.middle_index]
        self.answer = self.entry if self.task_type == "entry" else self.middle
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, k=self.k, middle=self.middle_index + 1)

    def solve(self):
        steps = []
        for index, row in enumerate(self.rows[1:], 1):
            shown = ", ".join(str(value) for value in row)
            steps.append(texts.t("s2", self.language, i=index, row=shown))
        steps.append(texts.t("s3", self.language, entry=self.entry, middle=self.middle))
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
