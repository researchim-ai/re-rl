"""DecisionStumpTask — лучший одномерный порог.

Точки (x, метка 0 или 1). Порог предсказывает 1 по одну сторону от границы.
Ответ — минимум ошибок среди всех порогов и обоих направлений, включая постоянные классификаторы.
"""

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
        ru = language == "ru"
        shown = ", ".join(f"({x}, {y})" for x, y in self.points)
        return ((f"Точки (x, метка): {shown}. Классификатор сравнивает x с порогом и может смотреть в любую сторону. "
                 f"Разрешены и постоянные ответы. Найдите минимальное число ошибок.") if ru else
                (f"Points (x, label): {shown}. A classifier compares x with a threshold and may face either way. "
                 f"Constant predictions are allowed. Find the minimum number of mistakes."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Перебор порогов и обоих направлений даёт {self.answer} ошибок.") if ru else
             (f"Searching thresholds and both directions gives {self.answer} mistakes.")),
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
