"""CoolTicksTask — остывание целыми тактами к температуре комнаты.

За такт температура теряет целую часть разности с комнатой, делённой на делитель.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cool_trace(temp: int, room: int, divisor: int, ticks: int) -> List[Tuple[int, int]]:
    trace = []
    for _ in range(ticks):
        temp = temp - (temp - room) // divisor
        trace.append((temp, temp - room))
    return trace


class CoolTicksTask(BaseMathTask):
    TASK_TYPE = "cool_ticks"
    TASK_TYPES = ["temp", "gap"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "d": 2}, 2: {"n": 3, "d": 2}, 3: {"n": 4, "d": 2},
        4: {"n": 5, "d": 3}, 5: {"n": 6, "d": 3}, 6: {"n": 7, "d": 3},
        7: {"n": 8, "d": 4}, 8: {"n": 10, "d": 4}, 9: {"n": 12, "d": 4},
        10: {"n": 14, "d": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.divisor = max(2, int(p["d"]))
        self.room = random.randint(0, 5)
        self.temp0 = self.room + random.randint(1, 12)
        self.trace = cool_trace(self.temp0, self.room, self.divisor, self.n)
        self.temp, self.gap = self.trace[-1]
        self.answer = self.temp if self.task_type == "temp" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(
            key, language, temp=self.temp0, room=self.room, divisor=self.divisor, n=self.n,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, temp=temp, gap=gap)
            for index, (temp, gap) in enumerate(self.trace, 1)
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
