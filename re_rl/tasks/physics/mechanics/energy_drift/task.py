"""EnergyDriftTask — две схемы осциллятора и сравнение их энергий.

Явный и полунеявный шаги идут из одной начальной точки. Энергию считает SymPy.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def osc_energy(place: int, speed: int, ticks: int) -> List[Tuple[int, int]]:
    explicit_place = sp.Integer(place)
    explicit_speed = sp.Integer(speed)
    semi_place = sp.Integer(place)
    semi_speed = sp.Integer(speed)
    trace = []
    for _ in range(ticks):
        previous = explicit_speed
        explicit_speed = explicit_speed - explicit_place
        explicit_place = explicit_place + previous
        semi_speed = semi_speed - semi_place
        semi_place = semi_place + semi_speed
        explicit = explicit_place ** 2 + explicit_speed ** 2
        semi = semi_place ** 2 + semi_speed ** 2
        trace.append((int(explicit), int(semi)))
    return trace


class EnergyDriftTask(BaseMathTask):
    TASK_TYPE = "energy_drift"
    TASK_TYPES = ["semi", "gap"]

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
        self.place = random.randint(-4, 6)
        self.speed = random.randint(-3, 4)
        if self.place == 0 and self.speed == 0:
            self.place = 1
        self.trace = osc_energy(self.place, self.speed, self.n)
        self.explicit = self.trace[-1][0]
        self.semi = self.trace[-1][1]
        self.gap = self.explicit - self.semi
        self.answer = self.semi if self.task_type == "semi" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "semi" else "s1"
        return texts.t(key, language, n=self.n, place=self.place, speed=self.speed)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, explicit=explicit, semi=semi)
            for index, (explicit, semi) in enumerate(self.trace, 1)
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
