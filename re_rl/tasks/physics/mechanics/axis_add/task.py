"""AxisAddTask — момент инерции составного тела по теореме Штейнера.

Вклад части равен её собственному моменту плюс масса, умноженная на квадрат расстояния до оси.
Число частей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Part = Tuple[int, int, int]


def axis_trace(parts: Sequence[Part]) -> List[Tuple[int, int, int]]:
    shift_sum = 0
    total = 0
    trace = []
    for own, mass, distance in parts:
        if own < 0 or mass <= 0:
            raise RuntimeError("axis mismatch")
        shift = mass * distance * distance
        total += own + shift
        shift_sum += shift
        trace.append((shift, total, shift_sum))
    return trace


class AxisAddTask(BaseMathTask):
    TASK_TYPE = "axis_add"
    TASK_TYPES = ["inertia", "shift"]

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
        self.parts = [
            (random.randint(0, 6), random.randint(1, 5), random.randint(0, 4))
            for _ in range(self.n)
        ]
        self.trace = axis_trace(self.parts)
        self.inertia = self.trace[-1][1]
        self.shift = self.trace[-1][2]
        self.answer = self.inertia if self.task_type == "inertia" else self.shift
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{own} {mass} {distance}" for own, mass, distance in self.parts)

    def _descr(self, language):
        key = "s0" if self.task_type == "inertia" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, shift=shift, inertia=inertia, moved=moved)
            for index, (shift, inertia, moved) in enumerate(self.trace, 1)
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
