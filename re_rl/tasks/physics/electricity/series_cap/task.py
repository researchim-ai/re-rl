"""SeriesCapTask — последовательные конденсаторы с общим зарядом.

Напряжение конденсатора — заряд, делённый на ёмкость. Энергия — квадрат заряда, делённый на удвоенную ёмкость.
Число конденсаторов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cap_divisors(charge: int) -> List[int]:
    return [value for value in range(1, charge + 1) if charge % value == 0]


def cap_trace(charge: int, caps: Sequence[int]) -> List[Tuple[int, int]]:
    voltage = 0
    energy = 0
    trace = []
    for cap in caps:
        voltage += charge // cap
        energy += (charge * charge) // (2 * cap)
        trace.append((voltage, energy))
    return trace


class SeriesCapTask(BaseMathTask):
    TASK_TYPE = "series_cap"
    TASK_TYPES = ["voltage", "energy"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "q": 12}, 2: {"n": 2, "q": 12}, 3: {"n": 3, "q": 12},
        4: {"n": 4, "q": 24}, 5: {"n": 5, "q": 24}, 6: {"n": 6, "q": 24},
        7: {"n": 7, "q": 36}, 8: {"n": 8, "q": 36}, 9: {"n": 10, "q": 48},
        10: {"n": 12, "q": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.charge = max(2, int(p["q"]))
        choices = cap_divisors(self.charge)
        self.caps = [random.choice(choices) for _ in range(self.n)]
        self.trace = cap_trace(self.charge, self.caps)
        self.voltage, self.energy = self.trace[-1]
        self.answer = self.voltage if self.task_type == "voltage" else self.energy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(cap) for cap in self.caps)
        key = "s0" if self.task_type == "voltage" else "s1"
        return texts.t(key, language, n=self.n, charge=self.charge, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cap=cap, voltage=voltage, energy=energy)
            for index, (cap, (voltage, energy)) in enumerate(zip(self.caps, self.trace), 1)
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
