"""ModPolyTask — произведение в кольце многочленов над полем вычетов.

Коэффициент степени собирается из всех пар, дающих эту степень, и сокращается по модулю.
Число коэффициентов первого многочлена растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mod_conv(left: Sequence[int], right: Sequence[int], prime: int) -> List[Tuple[int, int]]:
    width = len(left) + len(right) - 1
    raw = [0] * width
    for i, coeff in enumerate(left):
        for j, other in enumerate(right):
            raw[i + j] = (raw[i + j] + coeff * other) % prime
    total = 0
    trace = []
    for coeff in raw:
        total = (total + coeff) % prime
        trace.append((coeff, total))
    return trace


class ModPolyTask(BaseMathTask):
    TASK_TYPE = "mod_poly"
    TASK_TYPES = ["coeff", "total"]
    PRIMES = (2, 3, 5, 7)

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
        self.prime = random.choice(self.PRIMES)
        self.left = [random.randint(0, self.prime - 1) for _ in range(self.n)]
        self.right = [random.randint(0, self.prime - 1) for _ in range(2)]
        if self.left[-1] == 0:
            self.left[-1] = 1
        if self.right[-1] == 0:
            self.right[-1] = 1
        self.trace = mod_conv(self.left, self.right, self.prime)
        self.k = random.randint(0, len(self.trace) - 1)
        self.coeff = self.trace[self.k][0]
        self.total = self.trace[-1][1]
        self.answer = self.coeff if self.task_type == "coeff" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, coeffs: Sequence[int]) -> str:
        return " ".join(str(coeff) for coeff in coeffs)

    def _descr(self, language):
        key = "s0" if self.task_type == "coeff" else "s1"
        return texts.t(
            key, language, n=self.n, prime=self.prime, left=self._row(self.left),
            right=self._row(self.right), k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, coeff=coeff, total=total)
            for index, (coeff, total) in enumerate(self.trace)
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
