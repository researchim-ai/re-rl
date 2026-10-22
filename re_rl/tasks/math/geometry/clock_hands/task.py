"""ClockHandsTask — меньший и больший углы между часовой и минутной стрелками.

Минута чётная, поэтому |30H − 5.5M| — целое число градусов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _minutes(mode: int) -> List[int]:
    if mode <= 0:
        return [0]
    if mode == 1:
        return [0, 30]
    return list(range(0, 60, 2))


class ClockHandsTask(BaseMathTask):
    TASK_TYPE = "clock_hands"
    TASK_TYPES = ["smaller", "larger"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mode": 0}, 2: {"mode": 0}, 3: {"mode": 1}, 4: {"mode": 1}, 5: {"mode": 2},
        6: {"mode": 2}, 7: {"mode": 2}, 8: {"mode": 2}, 9: {"mode": 2}, 10: {"mode": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.hour = random.randint(1, 11)
        self.minute = random.choice(_minutes(int(p["mode"])))
        self.raw = abs(60 * self.hour - 11 * self.minute) // 2
        self.smaller = min(self.raw, 360 - self.raw)
        self.larger = 360 - self.smaller
        self.answer = self.smaller if self.task_type == "smaller" else self.larger
        self.stamp = f"{self.hour}:{self.minute:02d}"
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "smaller" else "s1"
        return texts.t(key, language, stamp=self.stamp)

    def solve(self):
        step = texts.t(
            "s2", self.language, hour=self.hour, minute=self.minute,
            raw=self.raw, smaller=self.smaller, larger=self.larger,
        )
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
