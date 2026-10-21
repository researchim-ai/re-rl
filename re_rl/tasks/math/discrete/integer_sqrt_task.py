"""IntegerSqrtTask — целый квадратный корень и остаток.

q — наибольшее неотрицательное целое с q^2 <= n. Остаток равен n - q^2.
"""

import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def isqrt_pair(n: int) -> Tuple[int, int]:
    root = 0
    bit = 1 << (n.bit_length() + 1) // 2
    while bit:
        trial = root + bit
        if trial * trial <= n:
            root = trial
        bit >>= 1
    return root, n - root * root


class IntegerSqrtTask(BaseMathTask):
    TASK_TYPE = "integer_sqrt"
    TASK_TYPES = ["root", "remainder"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 30}, 2: {"m": 80}, 3: {"m": 200}, 4: {"m": 500}, 5: {"m": 2000},
        6: {"m": 8000}, 7: {"m": 30000}, 8: {"m": 100000}, 9: {"m": 400000},
        10: {"m": 1000000},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = random.randint(0, int(p["m"]))
        self.root, self.remainder = isqrt_pair(self.n)
        self.answer = self.root if self.task_type == "root" else self.remainder
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"q — наибольшее неотрицательное целое, для которого q^2 не превосходит {self.n}. "
                 f"Остаток равен {self.n} - q^2.") if ru else
                (f"q is the greatest nonnegative integer whose square does not exceed {self.n}. "
                 f"The remainder is {self.n} - q^2."))
        ask = (("Найдите q." if ru else "Find q.") if self.task_type == "root" else
               ("Найдите остаток." if ru else "Find the remainder."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        step = ((f"q = {self.root}, остаток {self.remainder}.") if ru else
                (f"q = {self.root}, remainder {self.remainder}."))
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
