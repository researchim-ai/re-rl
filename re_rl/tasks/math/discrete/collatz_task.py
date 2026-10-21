"""CollatzTask — шаги до единицы и максимум по дороге.

Чётное число делится на 2, нечётное заменяется на 3n+1. Старт входит в максимум.
"""

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
            raise RuntimeError("последовательность Коллатца не дошла до 1")
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
        ru = language == "ru"
        rule = (("Пока число больше 1: чётное делится на 2, нечётное заменяется на 3n + 1. "
                 "Максимум учитывает и стартовое число.") if ru else
                ("While the number is greater than 1: an even number is divided by 2, "
                 "an odd number becomes 3n + 1. The maximum includes the starting number."))
        if self.task_type == "steps":
            ask = ((f"Сколько шагов ведёт от {self.start} до 1?") if ru else
                   (f"How many steps lead from {self.start} to 1?"))
        else:
            ask = ((f"Какой максимум встретится на пути от {self.start} до 1?") if ru else
                   (f"What maximum occurs on the way from {self.start} to 1?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"От {self.start} до 1 нужно {self.steps} шагов, максимум {self.peak}.") if ru else
                (f"From {self.start} to 1 takes {self.steps} steps, maximum {self.peak}."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
