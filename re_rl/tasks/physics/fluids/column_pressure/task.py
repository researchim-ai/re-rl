"""ColumnPressureTask — давление столба из слоёв жидкости.

Вклад слоя — плотность, умноженная на 10 и на высоту. g равно 10.
Число слоёв растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Layer = Tuple[int, int]


def column_trace(layers: Sequence[Layer]) -> List[Tuple[int, int, int]]:
    pressure = 0
    best = -1
    which = 1
    trace = []
    for index, (density, height) in enumerate(layers, 1):
        piece = density * 10 * height
        pressure += piece
        if piece > best:
            best = piece
            which = index
        trace.append((piece, pressure, which))
    return trace


class ColumnPressureTask(BaseMathTask):
    TASK_TYPE = "column_pressure"
    TASK_TYPES = ["pressure", "layer"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.layers = [
            (random.randint(1, 4), random.randint(1, 5))
            for _ in range(self.n)
        ]
        self.trace = column_trace(self.layers)
        _, self.pressure, self.layer = self.trace[-1]
        self.answer = self.pressure if self.task_type == "pressure" else self.layer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{density}, {height}" for density, height in self.layers)
        key = "s0" if self.task_type == "pressure" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, piece=piece, pressure=pressure, layer=layer)
            for index, (piece, pressure, layer) in enumerate(self.trace, 1)
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
