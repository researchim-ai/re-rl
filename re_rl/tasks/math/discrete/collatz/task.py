"""CollatzTask — шаги до единицы и максимум по дороге.

Чётное число делится на 2, нечётное заменяется на 3n+1. Старт входит в максимум.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def collatz(start: int) -> Tuple[int, int]:
    value = start
    steps = 0
    peak = start
    while value != 1:
        value = value // 2 if value % 2 == 0 else 3 * value + 1
        steps += 1
        if value > peak:
            peak = value
        if steps > 100000:
            raise RuntimeError(texts.literal('literals.s4'))
    return steps, peak


class CollatzTask(BaseMathTask):
    TASK_TYPE = "collatz_steps"
    TASK_TYPES = ["steps", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 12}, 2: {"m": 25}, 3: {"m": 40}, 4: {"m": 80}, 5: {"m": 150},
        6: {"m": 300}, 7: {"m": 600}, 8: {"m": 1200}, 9: {"m": 2500}, 10: {"m": 5000},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.start = random.randint(1, int(p["m"]))
        self.steps, self.peak = collatz(self.start)
        self.answer = self.steps if self.task_type == "steps" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "steps":
            ask = ((texts.t('s2', language, start=self.start)))
        else:
            ask = ((texts.t('s3', language, start=self.start)))
        return f"{rule} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, start=self.start, steps=self.steps, peak=self.peak)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
