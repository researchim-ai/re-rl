"""SourceDistTask — расстояние до ближайшей пустой клетки.

Пустая клетка имеет расстояние 0. Расстояние считает SciPy.
В ряду есть хотя бы одна пустая клетка. Длина ряда растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import distance_transform_cdt

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def field_dist(mask: Sequence[int]) -> List[Tuple[int, int, int]]:
    dist = distance_transform_cdt(np.asarray(mask), metric="taxicab")
    total = 0
    peak = 0
    trace = []
    for value in dist:
        number = int(value)
        total += number
        peak = max(peak, number)
        trace.append((number, total, peak))
    return trace


class SourceDistTask(BaseMathTask):
    TASK_TYPE = "source_dist"
    TASK_TYPES = ["peak", "total"]

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
        self.mask = [random.randint(0, 1) for _ in range(self.n)]
        if sum(self.mask) == self.n:
            self.mask[random.randrange(self.n)] = 0
        self.trace = field_dist(self.mask)
        self.peak = self.trace[-1][2]
        self.total = self.trace[-1][1]
        self.answer = self.peak if self.task_type == "peak" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(bit) for bit in self.mask)
        key = "s0" if self.task_type == "peak" else "s1"
        return texts.t(key, language, n=self.n, mask=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, dist=dist, total=total, peak=peak)
            for index, (dist, total, peak) in enumerate(self.trace, 1)
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
