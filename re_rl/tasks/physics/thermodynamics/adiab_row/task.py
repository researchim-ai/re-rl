"""AdiabRowTask — цепочка адиабат одноатомного газа.

Показатель адиабаты 5/3. Шаг с целым k меняет объём в k^3 раз, температуру в k^2 раз и давление в k^5 раз.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def adiab_trace(pressure: int, volume: int, temperature: int, steps: Sequence[Step]) -> List[Tuple[int, int, int]]:
    if min(pressure, volume, temperature) <= 0 or pressure * volume % temperature:
        raise RuntimeError("adiab mismatch")
    amount = pressure * volume // temperature
    hold = temperature ** 3 * volume ** 2
    trace = []
    for kind, factor in steps:
        if factor < 2:
            raise RuntimeError("adiab mismatch")
        square = factor * factor
        cube = square * factor
        fifth = cube * square
        if kind == 0:
            if temperature % square or pressure % fifth:
                raise RuntimeError("adiab mismatch")
            temperature //= square
            volume *= cube
            pressure //= fifth
        elif kind == 1:
            if volume % cube:
                raise RuntimeError("adiab mismatch")
            temperature *= square
            volume //= cube
            pressure *= fifth
        else:
            raise RuntimeError("adiab mismatch")
        if temperature ** 3 * volume ** 2 != hold or pressure * volume != amount * temperature:
            raise RuntimeError("adiab mismatch")
        trace.append((temperature, pressure, volume))
    return trace


class AdiabRowTask(BaseMathTask):
    TASK_TYPE = "adiab_row"
    TASK_TYPES = ["temp", "pressure"]

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
        self.pressure, self.volume, self.temperature = self._start()
        self.trace = adiab_trace(self.pressure, self.volume, self.temperature, self.steps)
        self.temp = self.trace[-1][0]
        self.final_pressure = self.trace[-1][1]
        self.answer = self.temp if self.task_type == "temp" else self.final_pressure
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _start(self) -> Tuple[int, int, int]:
        credit_t = {2: 0, 3: 0}
        credit_v = {2: 0, 3: 0}
        credit_p = {2: 0, 3: 0}
        floor_t = {2: 0, 3: 0}
        floor_v = {2: 0, 3: 0}
        floor_p = {2: 0, 3: 0}
        for kind, factor in self.steps:
            if kind == 0:
                credit_t[factor] -= 1
                credit_p[factor] -= 1
                credit_v[factor] += 1
            else:
                credit_v[factor] -= 1
                credit_t[factor] += 1
                credit_p[factor] += 1
            floor_t[factor] = min(floor_t[factor], credit_t[factor])
            floor_v[factor] = min(floor_v[factor], credit_v[factor])
            floor_p[factor] = min(floor_p[factor], credit_p[factor])
        temperature = pressure = volume = 1
        for factor in (2, 3):
            temperature *= factor ** (2 * -floor_t[factor])
            volume *= factor ** (3 * -floor_v[factor])
            pressure *= factor ** (5 * -floor_p[factor])
        return pressure, volume, temperature

    def _listing(self) -> str:
        return "; ".join(f"{kind} {factor}" for kind, factor in self.steps)

    def _descr(self, language):
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(
            key, language, n=self.n, pressure=self.pressure, volume=self.volume,
            temperature=self.temperature, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, temperature=temperature, pressure=pressure, volume=volume,
            )
            for index, (temperature, pressure, volume) in enumerate(self.trace, 1)
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
