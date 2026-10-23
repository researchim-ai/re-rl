"""HeatStepsTask — порции тепла поднимают температуру целыми градусами.

Неизрасходованный остаток тепла копится до следующей порции.
Число порций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def heat_trace(temp: int, capacity: int, packets: Sequence[int]) -> List[Tuple[int, int, int]]:
    stored = 0
    trace = []
    for packet in packets:
        stored += packet
        gained = stored // capacity
        stored %= capacity
        temp += gained
        trace.append((gained, temp, stored))
    return trace


class HeatStepsTask(BaseMathTask):
    TASK_TYPE = "heat_steps"
    TASK_TYPES = ["temp", "stored"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "c": 3}, 2: {"n": 3, "c": 4}, 3: {"n": 4, "c": 4},
        4: {"n": 5, "c": 5}, 5: {"n": 6, "c": 5}, 6: {"n": 7, "c": 6},
        7: {"n": 8, "c": 6}, 8: {"n": 10, "c": 6}, 9: {"n": 12, "c": 8},
        10: {"n": 14, "c": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.capacity = max(1, int(p["c"]))
        self.temp0 = random.randint(0, 5)
        self.packets = [random.randint(0, self.capacity + 3) for _ in range(self.n)]
        self.trace = heat_trace(self.temp0, self.capacity, self.packets)
        _, self.temp, self.stored = self.trace[-1]
        self.answer = self.temp if self.task_type == "temp" else self.stored
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(packet) for packet in self.packets)
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(
            key, language, temp=self.temp0, capacity=self.capacity, n=self.n, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, packet=packet, gained=gained, temp=temp, stored=stored)
            for index, (packet, (gained, temp, stored)) in enumerate(zip(self.packets, self.trace), 1)
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
