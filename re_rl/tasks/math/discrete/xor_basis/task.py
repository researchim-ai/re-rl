"""XorBasisTask — ранг набора чисел по исключающему или.

Число вставляется в базис со старшего бита. Если бит уже занят, он вычитается по XOR.
Длина набора растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

BITS = 8


def _insert(basis: List[int], value: int) -> bool:
    for bit in range(BITS - 1, -1, -1):
        if (value >> bit) & 1 == 0:
            continue
        if basis[bit] == 0:
            basis[bit] = value
            return True
        value ^= basis[bit]
    return False


def _reachable(basis: List[int], target: int) -> int:
    value = target
    for bit in range(BITS - 1, -1, -1):
        if basis[bit] and ((value >> bit) & 1):
            value ^= basis[bit]
    return int(value == 0)


def xor_basis_trace(numbers: Sequence[int], target: int) -> List[Tuple[int, int]]:
    basis = [0] * BITS
    rank = 0
    trace = []
    for number in numbers:
        if _insert(basis, number):
            rank += 1
        trace.append((rank, _reachable(basis, target)))
    return trace


class XorBasisTask(BaseMathTask):
    TASK_TYPE = "xor_basis"
    TASK_TYPES = ["rank", "hit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.numbers = [random.randint(1, 31) for _ in range(self.n)]
        self.target = random.randint(1, 31)
        self.trace = xor_basis_trace(self.numbers, self.target)
        self.rank, self.hit = self.trace[-1]
        self.answer = self.rank if self.task_type == "rank" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.numbers)
        key = "s0" if self.task_type == "rank" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, target=self.target)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, rank=rank, hit=hit)
            for index, (value, (rank, hit)) in enumerate(zip(self.numbers, self.trace), 1)
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
