"""SplitEnergyTask — кинетическая и потенциальная части средней энергии.

Кинетическая часть — минус дискретный лапласиан. Потенциальная — потенциал на квадрат функции.
Их сумма совпадает со средним значением полного гамильтониана.
Число узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def virial_trace(psi: Sequence[int], potential: Sequence[int]) -> List[Tuple[int, int]]:
    kinetic = 0
    potential_energy = 0
    full = 0
    trace = []
    for index, value in enumerate(psi):
        left = psi[index - 1] if index else 0
        right = psi[index + 1] if index + 1 < len(psi) else 0
        kinetic_density = -left + 2 * value - right
        kinetic += value * kinetic_density
        potential_energy += potential[index] * value * value
        full += value * (kinetic_density + potential[index] * value)
        trace.append((kinetic, potential_energy))
    if kinetic + potential_energy != full:
        raise RuntimeError("energy mismatch")
    return trace


class SplitEnergyTask(BaseMathTask):
    TASK_TYPE = "split_energy"
    TASK_TYPES = ["kinetic", "potential"]

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
        self.psi = [random.randint(-2, 2) for _ in range(self.n)]
        if not any(self.psi):
            self.psi[0] = 1
        self.potential = [random.randint(-2, 3) for _ in range(self.n)]
        self.trace = virial_trace(self.psi, self.potential)
        self.kinetic = self.trace[-1][0]
        self.potential_energy = self.trace[-1][1]
        self.answer = self.kinetic if self.task_type == "kinetic" else self.potential_energy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "kinetic" else "s1"
        return texts.t(key, language, n=self.n, psi=self._row(self.psi), potential=self._row(self.potential))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kinetic=kinetic, potential=potential)
            for index, (kinetic, potential) in enumerate(self.trace, 1)
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
