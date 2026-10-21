"""PolynomialProductTask — произведение двух многочленов.

Коэффициенты даны от свободного члена к старшей степени.
Спрашивается один коэффициент произведения или его значение в целой точке.
"""

import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def poly_mul(left: Sequence[int], right: Sequence[int]) -> List[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, coeff in enumerate(left):
        for j, other in enumerate(right):
            out[i + j] += coeff * other
    return out


def poly_eval(coeffs: Sequence[int], point: int) -> int:
    acc = 0
    power = 1
    for coeff in coeffs:
        acc += coeff * power
        power *= point
    return acc


class PolynomialProductTask(BaseMathTask):
    TASK_TYPE = "polynomial_product"
    TASK_TYPES = ["coefficient", "value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 2, "mag": 3}, 2: {"d": 2, "mag": 4}, 3: {"d": 3, "mag": 4},
        4: {"d": 3, "mag": 5}, 5: {"d": 4, "mag": 5}, 6: {"d": 4, "mag": 6},
        7: {"d": 5, "mag": 6}, 8: {"d": 5, "mag": 7}, 9: {"d": 6, "mag": 7},
        10: {"d": 6, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        degree = int(p["d"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.left = [random.randint(-self.mag, self.mag) for _ in range(random.randint(1, degree))]
        self.right = [random.randint(-self.mag, self.mag) for _ in range(random.randint(1, degree))]
        self.product = poly_mul(self.left, self.right)
        self.power = random.randrange(len(self.product))
        self.point = random.randint(-3, 4)
        self.coefficient = self.product[self.power]
        self.value = poly_eval(self.product, self.point)
        self.answer = self.coefficient if self.task_type == "coefficient" else self.value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _coeffs(self, values: Sequence[int]) -> str:
        return " ".join(map(str, values))

    def _descr(self, language):
        ru = language == "ru"
        data = ((f"Коэффициенты A от свободного члена: {self._coeffs(self.left)}. "
                 f"Коэффициенты B: {self._coeffs(self.right)}.") if ru else
                (f"Coefficients of A from the constant term: {self._coeffs(self.left)}. "
                 f"Coefficients of B: {self._coeffs(self.right)}."))
        if self.task_type == "coefficient":
            ask = ((f"Найдите коэффициент произведения при степени {self.power}.") if ru else
                   (f"Find the coefficient of degree {self.power} in the product."))
        else:
            ask = ((f"Найдите значение произведения в точке {self.point}.") if ru else
                   (f"Find the value of the product at {self.point}."))
        return f"{data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = " ".join(map(str, self.product))
        step = ((f"Произведение: {shown}. В точке {self.point} получается {self.value}.") if ru else
                (f"Product: {shown}. At {self.point} it equals {self.value}."))
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
