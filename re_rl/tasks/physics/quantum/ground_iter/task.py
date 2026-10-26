"""GroundIterTask — степенной метод для основного состояния дискретной ямы.

Сдвиг 8 больше любого значения энергии при потенциале не выше 2.
Вектор (8I-H) умножается и сокращается на общий делитель.
Число узлов и итераций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

SHIFT = 8


def _apply(psi: Sequence[int], potential: Sequence[int]) -> List[int]:
    acted = []
    for index, center in enumerate(psi):
        left = psi[index - 1] if index else 0
        right = psi[index + 1] if index + 1 < len(psi) else 0
        acted.append(-left + 2 * center - right + potential[index] * center)
    return acted


def _gcd(values: Sequence[int]) -> int:
    common = 0
    for value in values:
        common = math.gcd(common, abs(value))
    return common or 1


def iterate_trace(potential: Sequence[int], steps: int) -> List[Tuple[int, int]]:
    state = [0] * len(potential)
    state[0] = 1
    trace = []
    for _ in range(steps):
        acted = _apply(state, potential)
        state = [SHIFT * value - local for value, local in zip(state, acted)]
        common = _gcd(state)
        state = [value // common for value in state]
        trace.append((state[0], sum(state)))
    return trace


class GroundIterTask(BaseMathTask):
    TASK_TYPE = "ground_iter"
    TASK_TYPES = ["head", "total"]

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
        self.potential = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = iterate_trace(self.potential, self.n)
        self.head = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.head if self.task_type == "head" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.potential)

    def _descr(self, language):
        key = "s0" if self.task_type == "head" else "s1"
        return texts.t(key, language, n=self.n, potential=self._listing(), shift=SHIFT)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, head=head, total=total)
            for index, (head, total) in enumerate(self.trace, 1)
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
