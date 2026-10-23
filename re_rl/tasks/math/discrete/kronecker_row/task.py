"""KroneckerRowTask — символ Кронекера по модулям от 1 до n.

Если общий делитель больше 1, символ равен 0. Двойки в модуле дают знак, дальше символ Якоби.
Число модулей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from sympy.functions.combinatorial.numbers import kronecker_symbol

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


def kronecker(number: int, modulus: int) -> Tuple[int, int, int, int, int]:
    common = math.gcd(number, modulus)
    if common != 1:
        return 0, common, 0, 1, modulus
    sign = 1
    twos = 0
    odd = modulus
    while odd % 2 == 0:
        odd //= 2
        twos += 1
        if number % 8 in (3, 5):
            sign = -sign
    jacob = 1 if odd == 1 else jacobi(number, odd)
    return sign * jacob, common, twos, sign, odd


def kronecker_trace(number: int, count: int) -> List[Tuple[int, int, int, int, int, int]]:
    total = 0
    trace = []
    for modulus in range(1, count + 1):
        symbol, common, twos, sign, odd = kronecker(number, modulus)
        total += symbol
        trace.append((symbol, total, common, twos, sign, odd))
    return trace


class KroneckerRowTask(BaseMathTask):
    TASK_TYPE = "kronecker_row"
    TASK_TYPES = ["sum", "symbol"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.number = random.randint(2, 12)
        self.trace = kronecker_trace(self.number, self.n)
        self.k = random.randint(1, self.n)
        self.symbol = self.trace[self.k - 1][0]
        self.sum = self.trace[-1][1]
        assert self.symbol == int(kronecker_symbol(self.number, self.k))
        self.answer = self.sum if self.task_type == "sum" else self.symbol
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "sum" else "s1"
        return texts.t(key, language, number=self.number, n=self.n, k=self.k)

    def solve(self):
        steps = []
        for modulus, (symbol, total, common, twos, sign, odd) in enumerate(self.trace, 1):
            steps.append(texts.t(
                "s2", self.language, m=modulus, symbol=symbol, total=total,
                common=common, twos=twos, sign=sign, odd=odd,
            ))
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
