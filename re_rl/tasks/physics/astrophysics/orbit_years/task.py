"""OrbitYearsTask — периоды планет при целых радиусах орбиты.

Период планеты с радиусным числом r равен r*r*r. У первой планеты это число равно 1.
Число планет растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def orbit_trace(radii: Sequence[int]) -> List[Tuple[int, int]]:
    base = radii[0] * radii[0] * radii[0]
    trace = []
    for radius in radii:
        period = radius * radius * radius
        trace.append((period, period // base))
    return trace


class OrbitYearsTask(BaseMathTask):
    TASK_TYPE = "orbit_years"
    TASK_TYPES = ["period", "years"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.radii = [1] + [random.randint(1, 5) for _ in range(self.n - 1)]
        self.trace = orbit_trace(self.radii)
        self.k = random.randint(1, self.n)
        self.period, self.years = self.trace[self.k - 1]
        self.answer = self.period if self.task_type == "period" else self.years
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(radius) for radius in self.radii)
        key = "s0" if self.task_type == "period" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, radius=radius, period=period, years=years)
            for index, (radius, (period, years)) in enumerate(zip(self.radii, self.trace), 1)
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
