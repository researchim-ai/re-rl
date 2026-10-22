"""TruckTripsTask — погрузка в заданном порядке без перестановки грузов.

Число грузов растёт с уровнем. Новый рейс начинается, только если очередной груз не влезает.
Сумма, делённая на вместимость, этот ответ не заменяет.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class TruckTripsTask(BaseMathTask):
    TASK_TYPE = "truck_trips"
    TASK_TYPES = ["trips", "leftover"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "c": 4}, 2: {"n": 3, "c": 4}, 3: {"n": 4, "c": 5},
        4: {"n": 4, "c": 5}, 5: {"n": 5, "c": 6}, 6: {"n": 6, "c": 6},
        7: {"n": 7, "c": 7}, 8: {"n": 8, "c": 7}, 9: {"n": 9, "c": 8},
        10: {"n": 10, "c": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.capacity = max(2, int(p["c"]))
        self.sizes: List[int] = [random.randint(1, self.capacity) for _ in range(self.n)]
        self.trace: List[Dict[str, int]] = []
        trips = 1
        load = 0
        for size in self.sizes:
            if load + size > self.capacity:
                trips += 1
                load = 0
            load += size
            self.trace.append({"size": size, "trip": trips, "load": load})
        self.trips = trips
        self.leftover = load
        self.answer = self.trips if self.task_type == "trips" else self.leftover
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.sizes)
        key = "s0" if self.task_type == "trips" else "s1"
        return texts.t(key, language, n=self.n, capacity=self.capacity, listing=listing)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=i, size=item["size"], trip=item["trip"],
                load=item["load"], capacity=self.capacity,
            )
            for i, item in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, trips=self.trips, leftover=self.leftover))
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
