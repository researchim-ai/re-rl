"""TurnSignsTask — левые и правые повороты ломаной.

Знак векторного произведения говорит, влево или вправо ушла следующая сторона.
Число поворотов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int]


def turn_trace(points: Sequence[Point]) -> List[Tuple[int, int, int]]:
    left = 0
    right = 0
    trace = []
    for index in range(1, len(points) - 1):
        x1, y1 = points[index - 1]
        x2, y2 = points[index]
        x3, y3 = points[index + 1]
        cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
        if cross > 0:
            left += 1
        elif cross < 0:
            right += 1
        trace.append((cross, left, right))
    return trace


class TurnSignsTask(BaseMathTask):
    TASK_TYPE = "turn_signs"
    TASK_TYPES = ["lefts", "rights"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.points = [
            (random.randint(-4, 4), random.randint(-4, 4))
            for _ in range(self.n + 2)
        ]
        self.trace = turn_trace(self.points)
        _, self.lefts, self.rights = self.trace[-1]
        self.answer = self.lefts if self.task_type == "lefts" else self.rights
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{x} {y}" for x, y in self.points)
        key = "s0" if self.task_type == "lefts" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cross=cross, lefts=lefts, rights=rights)
            for index, (cross, lefts, rights) in enumerate(self.trace, 1)
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
