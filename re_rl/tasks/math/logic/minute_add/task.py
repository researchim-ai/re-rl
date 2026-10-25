"""MinuteAddTask — прибавление минут с переносом часа.

60 минут дают один час. Час после 23 снова становится 0.
Число прибавлений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def minute_trace(hour: int, minute: int, adds: Sequence[int]) -> List[Tuple[int, int, int]]:
    carries = 0
    trace = []
    for add in adds:
        minute += add
        while minute >= 60:
            minute -= 60
            hour = (hour + 1) % 24
            carries += 1
        trace.append((minute, hour, carries))
    return trace


class MinuteAddTask(BaseMathTask):
    TASK_TYPE = "minute_add"
    TASK_TYPES = ["minute", "carries"]

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
        self.hour = random.randint(0, 23)
        self.minute = random.randint(0, 59)
        self.adds = [random.randint(1, 80) for _ in range(self.n)]
        self.trace = minute_trace(self.hour, self.minute, self.adds)
        self.final_minute = self.trace[-1][0]
        self.carries = self.trace[-1][2]
        self.answer = self.final_minute if self.task_type == "minute" else self.carries
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(add) for add in self.adds)
        key = "s0" if self.task_type == "minute" else "s1"
        return texts.t(key, language, n=self.n, hour=self.hour, minute=self.minute, adds=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, add=add, minute=minute, hour=hour, carries=carries)
            for index, (add, (minute, hour, carries)) in enumerate(zip(self.adds, self.trace), 1)
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
