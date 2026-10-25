"""ForceWorkTask — работа силы по соседним отсчётам.

Удвоенная работа отрезка равна сумме сил на концах. Накопление сверяется с трапециями SciPy.
Число отрезков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
from scipy.integrate import cumulative_trapezoid

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def work_trace(forces: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for left, right in zip(forces, forces[1:]):
        piece = left + right
        total += piece
        trace.append((piece, total))
    doubled = cumulative_trapezoid(np.asarray(forces, dtype=float), dx=1.0) * 2
    if not np.allclose(doubled, [item[1] for item in trace]):
        raise RuntimeError("trapezoid mismatch")
    return trace


class ForceWorkTask(BaseMathTask):
    TASK_TYPE = "force_work"
    TASK_TYPES = ["work", "piece"]

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
        self.forces = [random.randint(0, 8) for _ in range(self.n + 1)]
        self.trace = work_trace(self.forces)
        self.piece = self.trace[-1][0]
        self.work = self.trace[-1][1]
        self.answer = self.work if self.task_type == "work" else self.piece
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(force) for force in self.forces)
        key = "s0" if self.task_type == "work" else "s1"
        return texts.t(key, language, n=self.n, count=self.n + 1, forces=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, piece=piece, work=work)
            for index, (piece, work) in enumerate(self.trace, 1)
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
