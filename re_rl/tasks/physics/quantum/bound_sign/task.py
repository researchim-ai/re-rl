"""BoundSignTask — поиск стационарных энергий стрельбой.

Правый край волны меняет знак, когда пробная энергия проходит собственное значение.
Яма из четырёх узлов, число проб растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _edge(potential: Sequence[int], energy: int) -> int:
    previous = 0
    current = 1
    for value in potential:
        previous, current = current, 2 * current - previous + (value - energy) * current
    return current


def bound_trace(potential: Sequence[int], energies: Sequence[int]) -> List[Tuple[int, int]]:
    found = 0
    previous = None
    trace = []
    for energy in energies:
        edge = _edge(potential, energy)
        if edge == 0:
            found += 1
        elif previous not in (None, 0) and (previous > 0) != (edge > 0):
            found += 1
        previous = edge
        trace.append((edge, found))
    return trace


class BoundSignTask(BaseMathTask):
    TASK_TYPE = "bound_sign"
    TASK_TYPES = ["found", "edge"]
    WELL = 4

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
        self.potential = [random.randint(-1, 2) for _ in range(self.WELL)]
        self.energies = sorted(random.sample(range(-4, 12), self.n))
        self.trace = bound_trace(self.potential, self.energies)
        self.found = self.trace[-1][1]
        self.edge = self.trace[-1][0]
        self.answer = self.found if self.task_type == "found" else self.edge
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "found" else "s1"
        return texts.t(
            key, language, n=self.n, potential=self._row(self.potential),
            energies=self._row(self.energies),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, energy=energy, edge=edge, found=found)
            for index, ((edge, found), energy) in enumerate(zip(self.trace, self.energies), 1)
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
