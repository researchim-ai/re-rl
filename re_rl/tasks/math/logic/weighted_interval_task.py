"""WeightedIntervalTask — взвешенное расписание интервалов.

Интервалы совместимы, если конец предыдущего не позже начала следующего.
Нужна максимальная сумма прибылей. Непересекающийся жадный выбор по числу
работ здесь не подходит: у работ разные прибыли.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Job = Tuple[int, int, int]


def max_weighted(jobs: List[Job]) -> int:
    ordered = sorted(jobs, key=lambda job: (job[1], job[0]))
    n = len(ordered)
    prev = [-1] * n
    for i in range(n):
        for j in range(i - 1, -1, -1):
            if ordered[j][1] <= ordered[i][0]:
                prev[i] = j
                break
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        take = ordered[i - 1][2]
        if prev[i - 1] != -1:
            take += dp[prev[i - 1] + 1]
        dp[i] = max(dp[i - 1], take)
    return dp[n]


class WeightedIntervalTask(BaseMathTask):
    TASK_TYPE = "weighted_interval"
    TASK_TYPES = ["profit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "span": 8, "profit": 8}, 2: {"n": 4, "span": 10, "profit": 9},
        3: {"n": 4, "span": 12, "profit": 10}, 4: {"n": 5, "span": 14, "profit": 12},
        5: {"n": 6, "span": 16, "profit": 12}, 6: {"n": 6, "span": 18, "profit": 14},
        7: {"n": 7, "span": 20, "profit": 15}, 8: {"n": 8, "span": 22, "profit": 16},
        9: {"n": 9, "span": 24, "profit": 18}, 10: {"n": 10, "span": 28, "profit": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.span = int(p["span"])
        self.profit_max = int(p["profit"])
        self.task_type = "profit"
        self.augment = augment
        self.jobs: List[Job] = []
        for _ in range(self.n):
            start = random.randint(0, self.span - 1)
            end = random.randint(start + 1, self.span)
            self.jobs.append((start, end, random.randint(1, self.profit_max)))
        self.answer = max_weighted(self.jobs)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(f"({s}, {e}, {p})" for s, e, p in self.jobs)
        return ((f"Работы заданы тройками (начало, конец, прибыль): {shown}. "
                 f"Две работы совместимы, если конец одной не позже начала другой. "
                 f"Найдите максимальную суммарную прибыль.") if ru else
                (f"Jobs are triples (start, end, profit): {shown}. "
                 f"Two jobs are compatible when one ends no later than the other starts. "
                 f"Find the maximum total profit."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Динамика по работам, упорядоченным по концу, даёт {self.answer}.") if ru else
             (f"DP over jobs sorted by end time gives {self.answer}.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
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
