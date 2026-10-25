"""IsingPassTask — один проход по цепочке спинов.

Спин переворачивается, если он смотрит против суммы соседей. Крайний спин имеет одного соседа.
Проход идёт слева направо, энергия связей считается NumPy. Число спинов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def bond_energy(spins: Sequence[int]) -> int:
    row = np.asarray(spins, dtype=np.int64)
    return int(-(row[:-1] * row[1:]).sum())


def ising_trace(spins: Sequence[int]) -> List[Tuple[int, int]]:
    row = [int(spin) for spin in spins]
    flips = 0
    trace = []
    for index in range(len(row)):
        left = row[index - 1] if index else 0
        right = row[index + 1] if index + 1 < len(row) else 0
        if row[index] * (left + right) < 0:
            row[index] = -row[index]
            flips += 1
        trace.append((flips, bond_energy(row)))
    return trace


class IsingPassTask(BaseMathTask):
    TASK_TYPE = "ising_pass"
    TASK_TYPES = ["flips", "energy"]

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
        self.spins = [random.choice((-1, 1)) for _ in range(self.n)]
        self.trace = ising_trace(self.spins)
        self.flips = self.trace[-1][0]
        self.energy = self.trace[-1][1]
        self.answer = self.flips if self.task_type == "flips" else self.energy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(spin) for spin in self.spins)
        key = "s0" if self.task_type == "flips" else "s1"
        return texts.t(key, language, n=self.n, spins=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, flips=flips, energy=energy)
            for index, (flips, energy) in enumerate(self.trace, 1)
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
