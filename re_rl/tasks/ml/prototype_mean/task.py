"""PrototypeMeanTask — онлайн-центроиды двух классов.

Сумма и число примеров класса копятся по одному объекту. Близость сравнивается без деления.
Число объектов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def prototype_trace(points: Sequence[Point]) -> List[Tuple[int, int, int, int]]:
    sums = [0, 0]
    counts = [0, 0]
    trace = []
    for value, label in points:
        sums[label] += value
        counts[label] += 1
        trace.append((sums[0], counts[0], sums[1], counts[1]))
    return trace


def nearer_class(query: int, sums: Sequence[int], counts: Sequence[int]) -> int:
    left = abs(sums[0] - query * counts[0]) * counts[1]
    right = abs(sums[1] - query * counts[1]) * counts[0]
    return 1 if left <= right else 2


class PrototypeMeanTask(BaseMathTask):
    TASK_TYPE = "prototype_mean"
    TASK_TYPES = ["total", "label"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "m": 4}, 2: {"n": 4, "m": 4}, 3: {"n": 5, "m": 5},
        4: {"n": 6, "m": 5}, 5: {"n": 7, "m": 6}, 6: {"n": 8, "m": 6},
        7: {"n": 9, "m": 6}, 8: {"n": 10, "m": 7}, 9: {"n": 12, "m": 7},
        10: {"n": 14, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.points = [(random.randint(-limit, limit), random.randrange(2)) for _ in range(self.n)]
        self.points[0] = (self.points[0][0], 0)
        self.points[1] = (self.points[1][0], 1)
        self.trace = prototype_trace(self.points)
        self.sums = [self.trace[-1][0], self.trace[-1][2]]
        self.counts = [self.trace[-1][1], self.trace[-1][3]]
        self.query = random.randint(-limit, limit)
        self.k = random.randint(1, 2)
        self.total = self.sums[self.k - 1]
        self.label = nearer_class(self.query, self.sums, self.counts)
        self.answer = self.total if self.task_type == "total" else self.label
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{value}, {label + 1}" for value, label in self.points)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, query=self.query, k=self.k)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, value=value, label=label + 1,
                sum1=sum1, count1=count1, sum2=sum2, count2=count2,
            )
            for index, ((value, label), (sum1, count1, sum2, count2)) in enumerate(
                zip(self.points, self.trace), 1,
            )
        ]
        steps.append(texts.t(
            "s3", self.language, query=self.query, label=self.label, k=self.k, total=self.total,
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
