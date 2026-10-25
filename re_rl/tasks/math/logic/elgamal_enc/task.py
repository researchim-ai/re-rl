"""ElgamalEncTask — шифрование Эль-Гамаля по битам показателя.

Обе степени начинают с 1. На каждом бите они возводятся в квадрат, а при бите 1 умножаются на основание и на открытый ключ.
Число битов показателя растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_PRIMES = (17, 19, 23, 29, 31, 37, 41, 43, 47, 53)


def elgamal_trace(base: int, public: int, message: int, bits: Sequence[int],
                  prime: int) -> List[Tuple[int, int]]:
    hint = 1
    power = 1
    trace = []
    for bit in bits:
        hint = hint * hint % prime
        power = power * power % prime
        if bit:
            hint = hint * base % prime
            power = power * public % prime
        mask = message * power % prime
        trace.append((hint, mask))
    return trace


class ElgamalEncTask(BaseMathTask):
    TASK_TYPE = "elgamal_enc"
    TASK_TYPES = ["hint", "mask"]

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
        self.prime = random.choice(_PRIMES)
        self.base = random.randint(2, self.prime - 1)
        self.public = random.randint(1, self.prime - 1)
        self.message = random.randint(1, self.prime - 1)
        self.bits = [1] + [random.randint(0, 1) for _ in range(self.n - 1)]
        self.trace = elgamal_trace(self.base, self.public, self.message, self.bits, self.prime)
        self.hint = self.trace[-1][0]
        self.mask = self.trace[-1][1]
        self.answer = self.hint if self.task_type == "hint" else self.mask
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "hint" else "s1"
        return texts.t(key, language, p=self.prime, g=self.base, y=self.public,
                       m=self.message, n=self.n, bits=bits)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, hint=hint, mask=mask)
            for index, (bit, (hint, mask)) in enumerate(zip(self.bits, self.trace), 1)
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
