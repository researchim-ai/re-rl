"""PolyDivTask — деление многочленов столбиком.

Делитель приведённый степени 2, поэтому частное и остаток целые.
Коэффициенты записаны от старшей степени. Число шагов деления растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def poly_mul(left: Sequence[int], right: Sequence[int]) -> List[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, coeff in enumerate(left):
        for j, other in enumerate(right):
            out[i + j] += coeff * other
    return out


def poly_divmod(dividend: Sequence[int], divisor: Sequence[int]) -> Tuple[List[int], List[int]]:
    rest = list(dividend)
    quotient_length = len(dividend) - len(divisor) + 1
    quotient = []
    for index in range(quotient_length):
        coeff = rest[index]
        quotient.append(coeff)
        for shift, factor in enumerate(divisor):
            rest[index + shift] -= coeff * factor
    return quotient, rest[quotient_length:]


class PolyDivTask(BaseMathTask):
    TASK_TYPE = "poly_div"
    TASK_TYPES = ["quotient", "remainder"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 2}, 2: {"n": 2, "m": 3}, 3: {"n": 3, "m": 3},
        4: {"n": 3, "m": 3}, 5: {"n": 4, "m": 3}, 6: {"n": 5, "m": 4},
        7: {"n": 6, "m": 4}, 8: {"n": 7, "m": 4}, 9: {"n": 8, "m": 4},
        10: {"n": 10, "m": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.quotient = [random.randint(1, limit)]
        self.quotient.extend(random.randint(-limit, limit) for _ in range(self.n - 1))
        self.divisor = [1, random.randint(-limit, limit), random.randint(-limit, limit)]
        self.remainder = [random.randint(-limit, limit), random.randint(-limit, limit)]
        product = poly_mul(self.quotient, self.divisor)
        self.dividend = product[:]
        self.dividend[-2] += self.remainder[0]
        self.dividend[-1] += self.remainder[1]
        self.degree = random.randint(0, self.n - 1) if self.task_type == "quotient" else random.randint(0, 1)
        if self.task_type == "quotient":
            self.answer = self.quotient[(self.n - 1) - self.degree]
        else:
            self.answer = self.remainder[1 - self.degree]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self, coeffs: Sequence[int]) -> str:
        return ", ".join(str(coeff) for coeff in coeffs)

    def _descr(self, language):
        key = "s0" if self.task_type == "quotient" else "s1"
        return texts.t(
            key, language,
            dividend=self._shown(self.dividend),
            divisor=self._shown(self.divisor),
            degree=self.degree,
        )

    def solve(self):
        rest = list(self.dividend)
        steps = []
        for index in range(self.n):
            coeff = rest[index]
            for shift, factor in enumerate(self.divisor):
                rest[index + shift] -= coeff * factor
            shown = ", ".join(str(value) for value in rest)
            steps.append(texts.t("s2", self.language, i=index + 1, coef=coeff, rest=shown))
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
