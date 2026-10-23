"""HeatMixTask — последовательное смешивание при целой температуре.

Каждая порция подобрана так, что общее тепло делится на новую массу.
Спрашиваются конечная температура и наибольшая по ходу. Число порций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Sample = Tuple[int, int]


def mix_temperature(mass: int, temp: int, samples: Sequence[Sample]) -> List[Tuple[int, int, int]]:
    peak = temp
    trace = []
    for add_mass, add_temp in samples:
        new_mass = mass + add_mass
        heat = mass * temp + add_mass * add_temp
        assert heat % new_mass == 0
        temp = heat // new_mass
        mass = new_mass
        peak = max(peak, temp)
        trace.append((temp, peak, mass))
    return trace


class HeatMixTask(BaseMathTask):
    TASK_TYPE = "heat_mix"
    TASK_TYPES = ["temp", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.mass0 = random.randint(1, 4)
        self.temp0 = random.randint(0, 12)
        self.samples = []
        mass, temp = self.mass0, self.temp0
        for _ in range(self.n):
            add_mass = random.randint(1, 4)
            new_mass = mass + add_mass
            base = mass * temp
            if base % math.gcd(add_mass, new_mass) != 0:
                add_mass = 1
                new_mass = mass + 1
                base = mass * temp
            add_temp = None
            for candidate in range(new_mass + 1):
                if (base + add_mass * candidate) % new_mass == 0:
                    add_temp = candidate
                    break
            if add_temp is None:
                add_mass = 1
                new_mass = mass + 1
                add_temp = (-(mass * temp)) % new_mass
            self.samples.append((add_mass, add_temp))
            heat = mass * temp + add_mass * add_temp
            temp = heat // new_mass
            mass = new_mass
        self.trace = mix_temperature(self.mass0, self.temp0, self.samples)
        self.temp, self.peak, self.mass = self.trace[-1]
        self.answer = self.temp if self.task_type == "temp" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{add_mass}, {add_temp}" for add_mass, add_temp in self.samples)
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(key, language, mass=self.mass0, temp=self.temp0, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, add_mass=add_mass, add_temp=add_temp,
                    temp=temp, peak=peak, mass=mass)
            for index, ((add_mass, add_temp), (temp, peak, mass)) in enumerate(zip(self.samples, self.trace), 1)
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
