"""PipeFlowTask — давление в трубе переменного сечения.

Расход общий, скорость обратно пропорциональна площади. Плотность равна 2, ускорение свободного падения равно 1, поэтому сумма давления, квадрата скорости и удвоенной высоты постоянна.
Число сечений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pipe_trace(areas: Sequence[int], heights: Sequence[int], pressure: int, flux: int) -> List[Tuple[int, int, int]]:
    if len(areas) != len(heights) or pressure <= 0 or flux <= 0:
        raise RuntimeError("pipe mismatch")
    const = None
    total = 0
    trace = []
    for area, height in zip(areas, heights):
        if area <= 0 or height < 0 or flux % area:
            raise RuntimeError("pipe mismatch")
        speed = flux // area
        if const is None:
            const = pressure + speed * speed + 2 * height
            head = pressure
        else:
            head = const - speed * speed - 2 * height
        if head <= 0 or head + speed * speed + 2 * height != const:
            raise RuntimeError("pipe mismatch")
        total += speed
        trace.append((speed, head, total))
    return trace


class PipeFlowTask(BaseMathTask):
    TASK_TYPE = "pipe_flow"
    TASK_TYPES = ["pressure", "speed"]

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
        self.flux = random.randint(2, 8)
        divisors = [item for item in range(1, self.flux + 1) if self.flux % item == 0]
        self.areas = [random.choice(divisors) for _ in range(self.n)]
        self.heights = [random.randint(0, 4) for _ in range(self.n)]
        speeds = [self.flux // area for area in self.areas]
        need = max(speed * speed + 2 * height for speed, height in zip(speeds, self.heights))
        const = need + random.randint(1, 5)
        self.pressure = const - speeds[0] * speeds[0] - 2 * self.heights[0]
        self.trace = pipe_trace(self.areas, self.heights, self.pressure, self.flux)
        self.final_pressure = self.trace[-1][1]
        self.speed = self.trace[-1][2]
        self.answer = self.final_pressure if self.task_type == "pressure" else self.speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{area} {height}" for area, height in zip(self.areas, self.heights))

    def _descr(self, language):
        key = "s0" if self.task_type == "pressure" else "s1"
        return texts.t(
            key, language, n=self.n, flux=self.flux, pressure=self.pressure, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, pressure=pressure, total=total)
            for index, (speed, pressure, total) in enumerate(self.trace, 1)
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
