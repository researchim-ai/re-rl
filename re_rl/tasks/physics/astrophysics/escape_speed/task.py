"""EscapeSpeedTask — квадрат второй космической скорости.

Он равен запасу, делённому на радиус. Радиусы делят запас.
Число планет растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def escape_divisors(gravity: int) -> List[int]:
    return [value for value in range(1, gravity + 1) if gravity % value == 0]


def escape_trace(gravity: int, radii: Sequence[int]) -> List[Tuple[int, int]]:
    best = -1
    which = 1
    trace = []
    for index, radius in enumerate(radii, 1):
        speed2 = gravity // radius
        if speed2 > best:
            best = speed2
            which = index
        trace.append((speed2, which))
    return trace


class EscapeSpeedTask(BaseMathTask):
    TASK_TYPE = "escape_speed"
    TASK_TYPES = ["speed2", "which"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "g": 12}, 2: {"n": 2, "g": 12}, 3: {"n": 3, "g": 24},
        4: {"n": 4, "g": 24}, 5: {"n": 5, "g": 36}, 6: {"n": 6, "g": 36},
        7: {"n": 7, "g": 48}, 8: {"n": 8, "g": 48}, 9: {"n": 10, "g": 60},
        10: {"n": 12, "g": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.gravity = max(1, int(p["g"]))
        choices = escape_divisors(self.gravity)
        self.radii = [random.choice(choices) for _ in range(self.n)]
        self.trace = escape_trace(self.gravity, self.radii)
        self.k = random.randint(1, self.n)
        self.speed2 = self.trace[self.k - 1][0]
        self.which = self.trace[-1][1]
        self.answer = self.speed2 if self.task_type == "speed2" else self.which
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(radius) for radius in self.radii)
        key = "s0" if self.task_type == "speed2" else "s1"
        return texts.t(key, language, gravity=self.gravity, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, radius=radius, speed2=speed2, which=which)
            for index, (radius, (speed2, which)) in enumerate(zip(self.radii, self.trace), 1)
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
