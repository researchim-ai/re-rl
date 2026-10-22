"""KMeansRoundsTask — несколько раундов одномерной кластеризации.

Центр кластера — нижняя медиана его точек, поэтому он остаётся целым.
При равном расстоянии точка идёт в первый кластер. Число раундов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lower_median(values: List[int]) -> int:
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def cluster_rounds(points: List[int], rounds: int) -> List[Tuple[int, int, int]]:
    left = min(points)
    right = max(points)
    if left == right:
        right = left + 1
    trace = []
    for _ in range(rounds):
        group0 = []
        group1 = []
        for point in points:
            if abs(point - left) <= abs(point - right):
                group0.append(point)
            else:
                group1.append(point)
        if group0:
            left = lower_median(group0)
        if group1:
            right = lower_median(group1)
        trace.append((left, right, len(group0)))
    return trace


class KMeansRoundsTask(BaseMathTask):
    TASK_TYPE = "kmeans_rounds"
    TASK_TYPES = ["count", "center"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 4, "s": 6}, 2: {"n": 2, "m": 5, "s": 6},
        3: {"n": 3, "m": 5, "s": 8}, 4: {"n": 3, "m": 6, "s": 8},
        5: {"n": 4, "m": 6, "s": 10}, 6: {"n": 5, "m": 8, "s": 10},
        7: {"n": 5, "m": 8, "s": 12}, 8: {"n": 6, "m": 10, "s": 12},
        9: {"n": 7, "m": 10, "s": 14}, 10: {"n": 8, "m": 12, "s": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.points = [random.randint(0, int(p["s"])) for _ in range(max(2, int(p["m"])))]
        self.rounds = cluster_rounds(self.points, self.n)
        self.center, self.other, self.count = self.rounds[-1]
        self.answer = self.count if self.task_type == "count" else self.center
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.points)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, left=left, right=right, count=count)
            for i, (left, right, count) in enumerate(self.rounds, 1)
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
