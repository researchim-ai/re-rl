"""DerangeCountTask — перестановки без неподвижных точек.

!0 = 1, !1 = 0, дальше !k = (k-1)·(!(k-1) + !(k-2)).
Ровно k неподвижных точек: сочетание на k, остальные без неподвижных.
Число предметов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def derange_table(limit: int) -> List[int]:
    table = [1, 0]
    for k in range(2, limit + 1):
        table.append((k - 1) * (table[k - 1] + table[k - 2]))
    return table


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


class DerangeCountTask(BaseMathTask):
    TASK_TYPE = "derange_count"
    TASK_TYPES = ["none", "exact"]

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
        self.table = derange_table(self.n)
        self.fixed = random.randint(0, self.n)
        self.none = self.table[self.n]
        self.ways = binom(self.n, self.fixed)
        self.exact = self.ways * self.table[self.n - self.fixed]
        self.answer = self.none if self.task_type == "none" else self.exact
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "none":
            return texts.t("s0", language, n=self.n)
        return texts.t("s1", language, n=self.n, fixed=self.fixed)

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=k, count=count)
            for k, count in enumerate(self.table)
        ]
        if self.task_type == "exact":
            steps.append(texts.t(
                "s3", self.language, fixed=self.fixed, ways=self.ways, answer=self.exact,
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
