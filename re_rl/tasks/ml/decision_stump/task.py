"""DecisionStumpTask — лучший одномерный порог.

Точки (x, метка 0 или 1). Порог предсказывает 1 по одну сторону от границы.
Ответ — минимум ошибок среди всех порогов и обоих направлений, включая постоянные классификаторы.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def stump_errors(points: List[Point]) -> int:
    n = len(points)
    ones = sum(y for _, y in points)
    best = min(ones, n - ones)
    thresholds = sorted({x for x, _ in points})
    for threshold in thresholds:
        for positive_if_ge in (True, False):
            errors = 0
            for x, y in points:
                pred = int(x >= threshold) if positive_if_ge else int(x < threshold)
                errors += int(pred != y)
            if errors < best:
                best = errors
    return best


class DecisionStumpTask(BaseMathTask):
    TASK_TYPE = "decision_stump"
    TASK_TYPES = ["errors"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "span": 4}, 2: {"n": 5, "span": 5}, 3: {"n": 6, "span": 5},
        4: {"n": 6, "span": 6}, 5: {"n": 7, "span": 6}, 6: {"n": 8, "span": 7},
        7: {"n": 9, "span": 8}, 8: {"n": 10, "span": 8}, 9: {"n": 12, "span": 9},
        10: {"n": 14, "span": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.span = int(p["span"])
        self.task_type = "errors"
        self.augment = augment
        self.points = [(random.randint(0, self.span), random.randint(0, 1)) for _ in range(self.n)]
        self.answer = stump_errors(self.points)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"({x}, {y})" for x, y in self.points)
        return ((texts.t('s0', language, shown=shown)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
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
