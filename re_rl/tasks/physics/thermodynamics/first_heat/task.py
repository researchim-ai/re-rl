"""FirstHeatTask — тепло и работа цепочки изобар и изохор.

В этих единицах изменение внутренней энергии равно количеству вещества, умноженному на изменение температуры.
Количество вещества — это P V / T, и оно постоянно. Тепло равно сумме этого изменения и работы.
Число участков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def law_trace(pressure: int, volume: int, temperature: int, steps: Sequence[Step]) -> List[Tuple[int, int, int]]:
    if temperature <= 0 or pressure * volume % temperature:
        raise RuntimeError("heat mismatch")
    amount = pressure * volume // temperature
    start = temperature
    heat_sum = 0
    work_sum = 0
    trace = []
    for kind, param in steps:
        if param <= 0:
            raise RuntimeError("heat mismatch")
        old_temperature = temperature
        if kind == 1:
            if (volume * param) % temperature:
                raise RuntimeError("heat mismatch")
            new_volume = volume * param // temperature
            work = pressure * (new_volume - volume)
            volume = new_volume
            temperature = param
        elif kind == 2:
            if (pressure * param) % temperature:
                raise RuntimeError("heat mismatch")
            pressure = pressure * param // temperature
            temperature = param
            work = 0
        else:
            raise RuntimeError("heat mismatch")
        delta = amount * (temperature - old_temperature)
        heat = delta + work
        if pressure * volume != amount * temperature:
            raise RuntimeError("heat mismatch")
        heat_sum += heat
        work_sum += work
        trace.append((work, heat_sum, work_sum))
    if heat_sum != amount * (temperature - start) + work_sum:
        raise RuntimeError("heat mismatch")
    return trace


class FirstHeatTask(BaseMathTask):
    TASK_TYPE = "first_heat"
    TASK_TYPES = ["heat", "work"]

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
        self.temperature = random.randint(1, 4)
        self.pressure = random.randint(1, 5)
        self.volume = self.temperature * random.randint(1, 3)
        self.steps = self._processes()
        self.trace = law_trace(self.pressure, self.volume, self.temperature, self.steps)
        self.heat = self.trace[-1][1]
        self.work = self.trace[-1][2]
        self.answer = self.heat if self.task_type == "heat" else self.work
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _processes(self) -> List[Step]:
        pressure, volume, temperature = self.pressure, self.volume, self.temperature
        steps = []
        for _ in range(self.n):
            kind = random.choice((1, 2))
            if kind == 1:
                if temperature > 1 and temperature % 2 == 0 and volume % 2 == 0 and random.randrange(2):
                    param = temperature // 2
                else:
                    param = temperature * random.randint(2, 3)
                volume = volume * param // temperature
                temperature = param
            else:
                if temperature > 1 and temperature % 2 == 0 and pressure % 2 == 0 and random.randrange(2):
                    param = temperature // 2
                else:
                    param = temperature * random.randint(2, 3)
                pressure = pressure * param // temperature
                temperature = param
            steps.append((kind, param))
        return steps

    def _listing(self) -> str:
        return "; ".join(f"{kind} {param}" for kind, param in self.steps)

    def _descr(self, language):
        key = "s0" if self.task_type == "heat" else "s1"
        return texts.t(
            key, language, n=self.n, pressure=self.pressure, volume=self.volume,
            temperature=self.temperature, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, work=work, heat=heat, total=total)
            for index, (work, heat, total) in enumerate(self.trace, 1)
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
