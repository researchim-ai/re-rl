"""SecretShareTask — восстановление секрета Шамира по модулю простого.

Секрет — значение многочлена в нуле. Степень меньше числа точек, точки имеют разные x.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Share = Tuple[int, int]
_PRIMES = [7, 11, 13, 17, 19, 23, 29, 31]


def reconstruct(shares: Sequence[Share], prime: int) -> int:
    secret = 0
    for index, (x_value, y_value) in enumerate(shares):
        numerator = 1
        denominator = 1
        for other, (x_other, _) in enumerate(shares):
            if other == index:
                continue
            numerator = numerator * (-x_other) % prime
            denominator = denominator * (x_value - x_other) % prime
        weight = numerator * pow(denominator, -1, prime) % prime
        secret = (secret + y_value * weight) % prime
    return secret


class SecretShareTask(BaseMathTask):
    TASK_TYPE = "secret_share"
    TASK_TYPES = ["secret"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 2, "pi": 2}, 2: {"k": 2, "pi": 3}, 3: {"k": 2, "pi": 4},
        4: {"k": 3, "pi": 4}, 5: {"k": 3, "pi": 5}, 6: {"k": 3, "pi": 6},
        7: {"k": 3, "pi": 6}, 8: {"k": 4, "pi": 7}, 9: {"k": 4, "pi": 8},
        10: {"k": 4, "pi": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.k = int(p["k"])
        self.task_type = "secret"
        self.augment = augment
        self.prime = random.choice(_PRIMES[:int(p["pi"])])
        self.coeffs = [random.randrange(self.prime) for _ in range(self.k)]
        self.secret = self.coeffs[0]
        xs = random.sample(range(1, self.prime), self.k)
        self.shares = [(x, self._eval(x)) for x in xs]
        recovered = reconstruct(self.shares, self.prime)
        if recovered != self.secret:
            raise RuntimeError(texts.t('s2', language))
        self.answer = self.secret
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _eval(self, x_value: int) -> int:
        acc = 0
        power = 1
        for coeff in self.coeffs:
            acc = (acc + coeff * power) % self.prime
            power = power * x_value % self.prime
        return acc

    def _shown(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self.shares)

    def _descr(self, language):
        return ((texts.t('s0', language, prime=self.prime, k=self.k, v2=self._shown(), v3=self.prime - 1)))

    def solve(self):
        step = ((texts.t('s1', self.language, answer=self.answer)))
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
