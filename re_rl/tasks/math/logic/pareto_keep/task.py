"""ParetoKeepTask — точки, которые никто не вытеснил.

Вытеснение требует нехудшей платы, нехудшего качества и строгой разницы хотя бы в одной оценке.
Число точек растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def _displaces(left: Point, right: Point) -> bool:
    cheaper = left[0] <= right[0]
    better = left[1] >= right[1]
    strict = left[0] < right[0] or left[1] > right[1]
    return cheaper and better and strict


def pareto_trace(points: Sequence[Point]) -> List[Tuple[int, int]]:
    front: List[Point] = []
    trace = []
    for point in points:
        beaten = any(_displaces(other, point) for other in front)
        if beaten:
            kept = list(front)
        else:
            kept = [other for other in front if not _displaces(point, other)]
            kept.append(point)
        front = kept
        trace.append((len(front), sum(item[0] for item in front)))
    return trace


class ParetoKeepTask(BaseMathTask):
    TASK_TYPE = "pareto_keep"
    TASK_TYPES = ["count", "cost"]

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
        self.points = [
            (random.randint(0, 8), random.randint(0, 8)) for _ in range(self.n)
        ]
        self.trace = pareto_trace(self.points)
        self.count = self.trace[-1][0]
        self.cost = self.trace[-1][1]
        self.answer = self.count if self.task_type == "count" else self.cost
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{cost} {quality}" for cost, quality in self.points)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, count=count, cost=cost)
            for index, (count, cost) in enumerate(self.trace, 1)
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
