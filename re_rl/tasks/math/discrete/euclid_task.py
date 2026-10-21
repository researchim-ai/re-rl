"""EuclidTask — алгоритм Евклида.

Пока второе число не ноль, заменяем пару (a, b) на (b, a mod b).
Подтипы: сам НОД и число таких делений.
"""

import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def euclid(a: int, b: int) -> Tuple[int, int]:
    steps = 0
    while b:
        a, b = b, a % b
        steps += 1
    return a, steps


class EuclidTask(BaseMathTask):
    TASK_TYPE = "euclid_gcd"
    TASK_TYPES = ["gcd", "steps"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 30}, 2: {"m": 50}, 3: {"m": 80}, 4: {"m": 120}, 5: {"m": 200},
        6: {"m": 300}, 7: {"m": 500}, 8: {"m": 800}, 9: {"m": 1200}, 10: {"m": 2000},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.a = random.randint(2, limit)
        self.b = random.randint(1, self.a)
        self.gcd, self.steps = euclid(self.a, self.b)
        self.answer = self.gcd if self.task_type == "gcd" else self.steps
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Алгоритм Евклида: пока b не 0, пара (a, b) заменяется на (b, a mod b). "
                 "Каждая такая замена — один шаг.") if ru else
                ("The Euclidean algorithm replaces (a, b) with (b, a mod b) while b is not 0. "
                 "Each replacement is one step."))
        if self.task_type == "gcd":
            ask = ((f"Найдите НОД({self.a}, {self.b}).") if ru else
                   (f"Find gcd({self.a}, {self.b})."))
        else:
            ask = ((f"Сколько шагов сделает алгоритм Евклида для пары ({self.a}, {self.b})?") if ru else
                   (f"How many steps does the Euclidean algorithm take for the pair ({self.a}, {self.b})?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"НОД = {self.gcd}, шагов = {self.steps}.") if ru else
                (f"gcd = {self.gcd}, steps = {self.steps}."))
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
