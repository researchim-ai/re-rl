"""PoissonRowTask — итерации дискретного потенциала с зарядами.

Края равны нулю. Соседняя сумма считается свёрткой SciPy, затем берётся целая половина вместе с зарядом.
Число итераций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import convolve1d

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_KERNEL = np.array([1, 0, 1], dtype=np.int64)


def poisson_trace(rho: Sequence[int], sweeps: int) -> List[Tuple[int, int]]:
    charge = np.asarray(rho, dtype=np.int64)
    state = np.zeros_like(charge)
    middle = len(rho) // 2
    trace = []
    for _ in range(sweeps):
        neighbors = convolve1d(state, _KERNEL, mode="constant", cval=0)
        state = (neighbors + charge) // 2
        trace.append((int(state[middle]), int(state.sum())))
    return trace


class PoissonRowTask(BaseMathTask):
    TASK_TYPE = "poisson_row"
    TASK_TYPES = ["mid", "total"]
    WIDTH = 3

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
        self.rho = [random.randint(0, 6) for _ in range(self.WIDTH)]
        self.trace = poisson_trace(self.rho, self.n)
        self.mid = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.mid if self.task_type == "mid" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.rho)
        key = "s0" if self.task_type == "mid" else "s1"
        return texts.t(key, language, n=self.n, width=self.WIDTH, rho=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, mid=mid, total=total)
            for index, (mid, total) in enumerate(self.trace, 1)
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
