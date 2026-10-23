"""NeighborVoteTask — метка по большинству среди ближайших точек.

Точки лежат на прямой, расстояния до запроса различны.
Ближайшие добавляются по одному, большинство пересчитывается. При равенстве побеждает 0.
Число соседей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def nearest_votes(points: Sequence[Point], query: int, count: int):
    ordered = sorted(points, key=lambda point: abs(point[0] - query))
    chosen = ordered[:count]
    ones = 0
    zeros = 0
    label = 0
    flips = 0
    history = []
    for _x, mark in chosen:
        if mark:
            ones += 1
        else:
            zeros += 1
        current = 1 if ones > zeros else 0
        if history and current != label:
            flips += 1
        label = current
        history.append((ones, zeros, label, flips))
    return chosen, label, flips, history


class NeighborVoteTask(BaseMathTask):
    TASK_TYPE = "neighbor_vote"
    TASK_TYPES = ["label", "flips"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 1}, 2: {"n": 1}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 7}, 8: {"n": 7},
        9: {"n": 9}, 10: {"n": 11},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        if self.n % 2 == 0:
            self.n += 1
        self.query = 0
        distances = random.sample(range(1, self.n + 8), self.n + 2)
        self.points = [
            (random.choice((-1, 1)) * distance, random.randint(0, 1))
            for distance in distances
        ]
        self.chosen, self.label, self.flips, self.history = nearest_votes(
            self.points, self.query, self.n,
        )
        self.answer = self.label if self.task_type == "label" else self.flips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{x}:{label}" for x, label in self.points)
        key = "s0" if self.task_type == "label" else "s1"
        return texts.t(key, language, n=self.n, query=self.query, listing=listing)

    def solve(self):
        steps = []
        for index, ((x, mark), (ones, zeros, label, flips)) in enumerate(
            zip(self.chosen, self.history), 1,
        ):
            steps.append(texts.t(
                "s2", self.language, i=index, x=x, mark=mark,
                ones=ones, zeros=zeros, label=label, flips=flips,
            ))
        steps.append(texts.t("s3", self.language, label=self.label, flips=self.flips))
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
