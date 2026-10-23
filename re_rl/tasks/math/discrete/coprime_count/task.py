"""CoprimeCountTask — включение-исключение по простым.

Считаются числа от 1 до границы, не делящиеся ни на одно из данных простых.
Число простых растёт с уровнем, пустое множество даёт саму границу.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
Row = Tuple[int, int, int, int]


def inclusion_rows(limit: int, primes: Sequence[int]) -> List[Row]:
    rows = []
    free = 0
    count = len(primes)
    for mask in range(1 << count):
        prod = 1
        bits = 0
        for index in range(count):
            if mask >> index & 1:
                prod *= primes[index]
                bits += 1
        term = 0 if prod > limit else limit // prod
        signed = term if bits % 2 == 0 else -term
        free += signed
        rows.append((bits, prod, signed, free))
    return rows


class CoprimeCountTask(BaseMathTask):
    TASK_TYPE = "coprime_count"
    TASK_TYPES = ["free", "hit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "limit": 24}, 2: {"n": 2, "limit": 40},
        3: {"n": 3, "limit": 60}, 4: {"n": 3, "limit": 90},
        5: {"n": 4, "limit": 120}, 6: {"n": 4, "limit": 160},
        7: {"n": 5, "limit": 200}, 8: {"n": 5, "limit": 240},
        9: {"n": 6, "limit": 280}, 10: {"n": 6, "limit": 360},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.limit = max(1, int(p["limit"]))
        self.primes = sorted(random.sample(PRIMES, self.n))
        self.rows = inclusion_rows(self.limit, self.primes)
        self.free = self.rows[-1][3]
        self.hit = self.limit - self.free
        self.answer = self.free if self.task_type == "free" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(prime) for prime in self.primes)
        key = "s0" if self.task_type == "free" else "s1"
        return texts.t(key, language, limit=self.limit, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bits=bits, prod=prod, term=term, free=free)
            for index, (bits, prod, term, free) in enumerate(self.rows, 1)
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
