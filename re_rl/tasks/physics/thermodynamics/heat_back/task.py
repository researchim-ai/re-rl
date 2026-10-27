"""HeatBackTask — неявный шаг теплопроводности на трёх ячейках.

Концы теплоизолированы. Новая тройка связана со старой тремя линейными уравнениями, сумма сохраняется.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _solve_rod(old: Sequence[int]) -> List[int]:
    if len(old) != 3:
        raise RuntimeError("heat mismatch")
    first, second, third = (Fraction(item) for item in old)
    half = (first - third) / 2
    right = (second + 3 * third + half) / 4
    left = right + half
    mid = 2 * right - third
    solved = (left, mid, right)
    if any(item.denominator != 1 for item in solved):
        raise RuntimeError("heat mismatch")
    new = [int(item) for item in solved]
    a_new, b_new, c_new = new
    if (2 * a_new - b_new, -a_new + 3 * b_new - c_new, -b_new + 2 * c_new) != tuple(old):
        raise RuntimeError("heat mismatch")
    return new


def rod_trace(cells: Sequence[int], steps: int) -> List[Tuple[int, int, int, int]]:
    state = [int(item) for item in cells]
    if len(state) != 3:
        raise RuntimeError("heat mismatch")
    total = sum(state)
    previous_energy = sum(item * item for item in state)
    trace = []
    for _ in range(steps):
        low = min(state)
        high = max(state)
        state = _solve_rod(state)
        if sum(state) != total or any(item < low or item > high for item in state):
            raise RuntimeError("heat mismatch")
        energy = sum(item * item for item in state)
        if energy > previous_energy:
            raise RuntimeError("heat mismatch")
        previous_energy = energy
        trace.append((state[0], state[1], state[2], energy))
    return trace


class HeatBackTask(BaseMathTask):
    TASK_TYPE = "heat_back"
    TASK_TYPES = ["edge", "energy"]

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
        state = [random.randint(0, 4) for _ in range(3)]
        for _ in range(self.n):
            left, mid, right = state
            lap = [mid - left, left - 2 * mid + right, mid - right]
            state = [state[index] - lap[index] for index in range(3)]
        self.cells = state
        self.trace = rod_trace(self.cells, self.n)
        self.edge = self.trace[-1][2]
        self.energy = self.trace[-1][3]
        self.answer = self.edge if self.task_type == "edge" else self.energy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(item) for item in self.cells)

    def _descr(self, language):
        key = "s0" if self.task_type == "edge" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, mid=mid, right=right, energy=energy)
            for index, (left, mid, right, energy) in enumerate(self.trace, 1)
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
