"""MeltHeatTask — плавление льда и нагрев воды целыми порциями.

Тепло сначала плавит лёд. Остаток поднимает температуру воды, и он делится на массу воды.
Число порций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def melt_trace(ice: int, water: int, packets: Sequence[int]) -> List[Tuple[int, int, int]]:
    temp = 0
    trace = []
    for heat in packets:
        melted = heat if heat < ice else ice
        ice -= melted
        water += melted
        heat -= melted
        if water:
            temp += heat // water
        trace.append((temp, ice, water))
    return trace


class MeltHeatTask(BaseMathTask):
    TASK_TYPE = "melt_heat"
    TASK_TYPES = ["temp", "ice"]

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
        self.ice0 = random.randint(0, 8)
        self.water0 = random.randint(1, 4)
        self.packets = []
        ice, water = self.ice0, self.water0
        for _ in range(self.n):
            melted = random.randint(0, ice) if ice else 0
            degrees = 0 if melted < ice else random.randint(0, 3)
            heat = melted + (water + melted) * degrees
            self.packets.append(heat)
            ice -= melted
            water += melted
        self.trace = melt_trace(self.ice0, self.water0, self.packets)
        self.temp, self.ice, self.water = self.trace[-1]
        self.answer = self.temp if self.task_type == "temp" else self.ice
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.packets)
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(
            key, language, ice=self.ice0, water=self.water0, n=self.n, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, heat=heat, temp=temp, ice=ice, water=water)
            for index, (heat, (temp, ice, water)) in enumerate(zip(self.packets, self.trace), 1)
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
