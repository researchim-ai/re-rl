"""KeplerRowTask — цепочка орбит с законом Кеплера.

Квадрат периода равен кубу радиуса. Шаг с целым k умножает радиус на k в квадрате и период на k в кубе, либо делит, если делится.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def kepler_trace(radius: int, period: int, steps: Sequence[Step]) -> List[Tuple[int, int]]:
    if radius <= 0 or period <= 0 or period * period != radius ** 3:
        raise RuntimeError("orbit mismatch")
    trace = []
    for kind, factor in steps:
        if factor < 2:
            raise RuntimeError("orbit mismatch")
        square = factor * factor
        cube = square * factor
        if kind == 0:
            radius *= square
            period *= cube
        elif kind == 1:
            if radius % square or period % cube:
                raise RuntimeError("orbit mismatch")
            radius //= square
            period //= cube
        else:
            raise RuntimeError("orbit mismatch")
        if period * period != radius ** 3:
            raise RuntimeError("orbit mismatch")
        trace.append((radius, period))
    return trace


class KeplerRowTask(BaseMathTask):
    TASK_TYPE = "kepler_row"
    TASK_TYPES = ["period", "radius"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 8}, 10: {"n": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.steps = [(random.choice((0, 1)), random.choice((2, 3))) for _ in range(self.n)]
        self.radius, self.period = self._start()
        self.trace = kepler_trace(self.radius, self.period, self.steps)
        self.final_radius = self.trace[-1][0]
        self.final_period = self.trace[-1][1]
        self.answer = self.final_period if self.task_type == "period" else self.final_radius
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _start(self) -> Tuple[int, int]:
        credit = {2: 0, 3: 0}
        floor = {2: 0, 3: 0}
        for kind, factor in self.steps:
            credit[factor] += 1 if kind == 0 else -1
            floor[factor] = min(floor[factor], credit[factor])
        radius = period = 1
        for factor in (2, 3):
            power = -floor[factor]
            radius *= factor ** (2 * power)
            period *= factor ** (3 * power)
        return radius, period

    def _listing(self) -> str:
        return "; ".join(f"{kind} {factor}" for kind, factor in self.steps)

    def _descr(self, language):
        key = "s0" if self.task_type == "period" else "s1"
        return texts.t(
            key, language, n=self.n, radius=self.radius, period=self.period, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, radius=radius, period=period)
            for index, (radius, period) in enumerate(self.trace, 1)
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
