"""KaprekarStepTask — несколько шагов разности Капрекара.

Число дополняется нулями слева до фиксированной ширины, цифры сортируются
по убыванию и по возрастанию, из большего вычитается меньшее.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def kaprekar_once(value: int, width: int) -> int:
    text = f"{value:0{width}d}"
    high = int("".join(sorted(text, reverse=True)))
    low = int("".join(sorted(text)))
    return high - low


def kaprekar_trace(start: int, width: int, rounds: int) -> List[int]:
    value = start
    trace = []
    for _ in range(rounds):
        value = kaprekar_once(value, width)
        trace.append(value)
    return trace


class KaprekarStepTask(BaseMathTask):
    TASK_TYPE = "kaprekar_step"
    TASK_TYPES = ["value", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "w": 2}, 2: {"n": 2, "w": 2}, 3: {"n": 3, "w": 3},
        4: {"n": 3, "w": 3}, 5: {"n": 4, "w": 3}, 6: {"n": 5, "w": 4},
        7: {"n": 6, "w": 4}, 8: {"n": 6, "w": 4}, 9: {"n": 7, "w": 4},
        10: {"n": 8, "w": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.width = max(2, int(p["w"]))
        span = 10 ** self.width
        self.start = random.randint(0, span - 1)
        if len(set(f"{self.start:0{self.width}d}")) == 1:
            self.start = 1 if self.start == 0 else self.start - 1
        self.trace = kaprekar_trace(self.start, self.width, self.n)
        self.value = self.trace[-1]
        self.peak = max(self.trace)
        self.answer = self.value if self.task_type == "value" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, start=self.start, width=self.width, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.trace, 1)
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
