"""ShockJumpTask — прямой скачок уплотнения идеального газа.

Показатель адиабаты 5/3. Плотность за скачком ищется как наименьшее целое,
при котором сходятся масса, импульс и энергия Ренкина–Гюгонио.
Число скачков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

State = Tuple[int, int, int]
CAP = 4


def _downstream(rho: int, speed: int, pressure: int) -> Optional[Tuple[int, int]]:
    flux = rho * speed
    for rho2 in range(rho + 1, CAP * rho + 1):
        if flux % rho2:
            continue
        speed2 = flux // rho2
        pressure2 = pressure + rho * speed * speed - rho2 * speed2 * speed2
        if pressure2 <= 0:
            continue
        left = 5 * pressure * rho2 + speed * speed * rho * rho2
        right = 5 * pressure2 * rho + speed2 * speed2 * rho * rho2
        if left == right:
            return rho2, pressure2
    return None


def _catalog(limit: int = 16) -> List[State]:
    found = []
    for rho in range(1, limit + 1):
        for speed in range(1, limit + 1):
            for pressure in range(1, limit + 1):
                if _downstream(rho, speed, pressure) is not None:
                    found.append((rho, speed, pressure))
    return found


SHOCKS = _catalog()


def hugoniot_trace(upstreams: Sequence[State]) -> List[Tuple[int, int]]:
    trace = []
    for rho, speed, pressure in upstreams:
        downstream = _downstream(rho, speed, pressure)
        if downstream is None:
            raise RuntimeError("shock mismatch")
        trace.append(downstream)
    return trace


class ShockJumpTask(BaseMathTask):
    TASK_TYPE = "shock_jump"
    TASK_TYPES = ["pressure", "density"]

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
        self.upstreams = [random.choice(SHOCKS) for _ in range(self.n)]
        self.trace = hugoniot_trace(self.upstreams)
        self.pressure = self.trace[-1][1]
        self.density = sum(item[0] for item in self.trace)
        self.answer = self.pressure if self.task_type == "pressure" else self.density
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{rho} {speed} {pressure}" for rho, speed, pressure in self.upstreams)

    def _descr(self, language):
        key = "s0" if self.task_type == "pressure" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, density=density, pressure=pressure)
            for index, (density, pressure) in enumerate(self.trace, 1)
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
