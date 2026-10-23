"""FirstRepeatTask — первое повторное значение в потоке.

Повтор — значение, которое уже встречалось раньше. Нумерация с 1.
Длина потока растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def repeat_trace(values: Sequence[int]) -> List[Tuple[int, int]]:
    seen = set()
    at = 0
    trace = []
    for index, value in enumerate(values, 1):
        if value in seen and at == 0:
            at = index
        seen.add(value)
        span = at - 1 if at else index
        trace.append((at, span))
    return trace


class FirstRepeatTask(BaseMathTask):
    TASK_TYPE = "first_repeat"
    TASK_TYPES = ["at", "span"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        width = max(2, self.n // 2)
        self.values = [random.randint(1, width) for _ in range(self.n)]
        self.trace = repeat_trace(self.values)
        self.at, self.span = self.trace[-1]
        self.answer = self.at if self.task_type == "at" else self.span
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "at" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, at=at, span=span)
            for index, (value, (at, span)) in enumerate(zip(self.values, self.trace), 1)
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
