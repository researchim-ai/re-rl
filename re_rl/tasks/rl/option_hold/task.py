"""OptionHoldTask — действие опции держится указанное число тактов.

Опции идут по порядку. Длина каждой не меньше 1.
Число опций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Option = Tuple[int, int]


def hold_trace(options: Sequence[Option]) -> List[int]:
    ticks = []
    for action, duration in options:
        ticks.extend([action] * duration)
    return ticks


class OptionHoldTask(BaseMathTask):
    TASK_TYPE = "option_hold"
    TASK_TYPES = ["tick", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 1}, 2: {"n": 3, "m": 1}, 3: {"n": 4, "m": 1},
        4: {"n": 4, "m": 2}, 5: {"n": 5, "m": 2}, 6: {"n": 5, "m": 2},
        7: {"n": 6, "m": 2}, 8: {"n": 6, "m": 2}, 9: {"n": 7, "m": 2},
        10: {"n": 8, "m": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        span = max(1, int(p["m"]))
        self.options = [
            (random.randint(1, 4), random.randint(1, span))
            for _ in range(self.n)
        ]
        self.ticks = hold_trace(self.options)
        self.total = len(self.ticks)
        self.k = random.randint(1, self.total)
        self.tick = self.ticks[self.k - 1]
        self.answer = self.tick if self.task_type == "tick" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{action}, {duration}" for action, duration in self.options)
        key = "s0" if self.task_type == "tick" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, action=action)
            for index, action in enumerate(self.ticks, 1)
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
