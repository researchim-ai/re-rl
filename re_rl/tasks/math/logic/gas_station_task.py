"""GasStationTask — с какой станции можно объехать кольцо.

На станции i добавляется gas[i] и тратится cost[i] до следующей.
Если суммарного бензина не хватает, ответ -1. Иначе стартовый индекс с 0
единственен: это станция сразу после самого глубокого отрицательного префикса.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def circuit_start(gas: List[int], cost: List[int]) -> int:
    if sum(gas) < sum(cost):
        return -1
    tank = 0
    start = 0
    for i, (got, need) in enumerate(zip(gas, cost)):
        tank += got - need
        if tank < 0:
            start = i + 1
            tank = 0
    return start


class GasStationTask(BaseMathTask):
    TASK_TYPE = "gas_station"
    TASK_TYPES = ["start"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 5}, 2: {"n": 4, "mag": 6}, 3: {"n": 4, "mag": 7},
        4: {"n": 5, "mag": 7}, 5: {"n": 5, "mag": 8}, 6: {"n": 6, "mag": 8},
        7: {"n": 6, "mag": 9}, 8: {"n": 7, "mag": 9}, 9: {"n": 8, "mag": 10},
        10: {"n": 9, "mag": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "start"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.gas = [random.randint(1, self.mag) for _ in range(self.n)]
        self.cost = [random.randint(1, self.mag) for _ in range(self.n)]
        if random.random() < 0.75 and sum(self.gas) < sum(self.cost):
            # Делаем кольцо проходимым, добавив запас на одну станцию.
            self.gas[0] += sum(self.cost) - sum(self.gas)
        self.answer = circuit_start(self.gas, self.cost)

    def _pairs(self) -> str:
        return ", ".join(f"({g}, {c})" for g, c in zip(self.gas, self.cost))

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Кольцевая дорога. На станциях пары (бензин, расход до следующей): {self._pairs()}. "
                 f"Индексы с 0. Найдите индекс станции, с которой можно объехать всё кольцо. "
                 f"Если это невозможно, ответьте -1.") if ru else
                (f"A circular road. Stations are pairs (gas, cost to the next): {self._pairs()}. "
                 f"Indices start at 0. Find the station index from which the whole circuit can be completed. "
                 f"If it is impossible, answer -1."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Сравнение сумм и сброс бака на отрицательном префиксе дают старт {self.answer}.") if ru else
             (f"Comparing the totals and resetting the tank on a negative prefix gives start {self.answer}.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
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
