"""CrtChainTask — система сравнений по попарно простым модулям.

Модули — первые простые числа. Решение подставляется по одному сравнению.
Число сравнений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)


def solve_crt(moduli: List[int], remainders: List[int]) -> Tuple[int, int, List[int]]:
    value = remainders[0]
    modulus = moduli[0]
    partial = [value]
    for mod, remainder in zip(moduli[1:], remainders[1:]):
        while value % mod != remainder:
            value += modulus
        modulus *= mod
        partial.append(value)
    return value, modulus, partial


class CrtChainTask(BaseMathTask):
    TASK_TYPE = "crt_chain"
    TASK_TYPES = ["value", "next"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5}, 9: {"n": 6}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.moduli = list(_PRIMES[:self.n])
        self.remainders = [random.randint(0, mod - 1) for mod in self.moduli]
        self.value, self.modulus, self.partial = solve_crt(self.moduli, self.remainders)
        self.answer = self.value if self.task_type == "value" else self.value + self.modulus
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [
            texts.t("s2", language, r=remainder, m=mod)
            for remainder, mod in zip(self.remainders, self.moduli)
        ]
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=" ".join(parts))

    def solve(self):
        steps = []
        modulus = 1
        for index, (mod, remainder, value) in enumerate(zip(self.moduli, self.remainders, self.partial), 1):
            modulus *= mod
            steps.append(texts.t("s3", self.language, i=index, r=remainder, m=mod, value=value, mod=modulus))
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
