"""JacobiRowTask — символы Якоби по нечётным модулям.

Символ считается квадратичным законом взаимности. Сумма может быть отрицательной.
Число модулей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def jacobi(number: int, modulus: int) -> int:
    result = 1
    number %= modulus
    while number:
        while number % 2 == 0:
            number //= 2
            if modulus % 8 in (3, 5):
                result = -result
        number, modulus = modulus, number
        if number % 4 == 3 and modulus % 4 == 3:
            result = -result
        number %= modulus
    return result if modulus == 1 else 0


def jacobi_trace(number: int, count: int) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for index in range(count):
        symbol = jacobi(number, 2 * index + 1)
        total += symbol
        trace.append((symbol, total))
    return trace


class JacobiRowTask(BaseMathTask):
    TASK_TYPE = "jacobi_row"
    TASK_TYPES = ["sum", "symbol"]

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
        self.number = random.randint(1, 9)
        self.trace = jacobi_trace(self.number, self.n)
        self.k = random.randint(1, self.n)
        self.symbol = self.trace[self.k - 1][0]
        self.sum = self.trace[-1][1]
        self.answer = self.sum if self.task_type == "sum" else self.symbol
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "sum" else "s1"
        modulus = 2 * self.k - 1
        return texts.t(key, language, number=self.number, n=self.n, k=self.k, modulus=modulus)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, modulus=2 * index - 1, symbol=symbol, total=total)
            for index, (symbol, total) in enumerate(self.trace, 1)
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
