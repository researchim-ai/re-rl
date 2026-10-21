"""NussinovTask — наибольшее число непересекающихся пар в РНК.

Пары только A-U и G-C, в любом порядке. Между концами пары стоят хотя бы три основания:
их номера отличаются минимум на 4. Пары не пересекаются.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_PAIRS = {("A", "U"), ("U", "A"), ("G", "C"), ("C", "G")}
_ALPHABET = "ACGU"


def can_pair(left: str, right: str) -> bool:
    return (left, right) in _PAIRS


def nussinov(seq: str) -> int:
    n = len(seq)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for length in range(1, n):
        for i in range(n - length):
            j = i + length
            best = dp[i + 1][j]
            best = max(best, dp[i][j - 1])
            if j - i >= 4 and can_pair(seq[i], seq[j]):
                best = max(best, dp[i + 1][j - 1] + 1)
            for k in range(i, j):
                best = max(best, dp[i][k] + dp[k + 1][j])
            dp[i][j] = best
    return dp[0][n - 1]


def brute_pairs(seq: str) -> int:
    """Перебор допустимых наборов пар. Для коротких строк в тестах."""
    n = len(seq)
    valid: list[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 4, n):
            if can_pair(seq[i], seq[j]):
                valid.append((i, j))
    best = 0
    for mask in range(1 << len(valid)):
        chosen = [valid[bit] for bit in range(len(valid)) if mask >> bit & 1]
        if _compatible(chosen):
            best = max(best, len(chosen))
    return best


def _compatible(pairs: list[Tuple[int, int]]) -> bool:
    used = set()
    for a, b in pairs:
        if a in used or b in used:
            return False
        used.add(a)
        used.add(b)
    ordered = sorted(pairs)
    for i, (a, b) in enumerate(ordered):
        for c, d in ordered[i + 1:]:
            if a < c < b < d:
                return False
    return True


class NussinovTask(BaseMathTask):
    TASK_TYPE = "nussinov"
    TASK_TYPES = ["pairs"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 7}, 3: {"n": 8}, 4: {"n": 9}, 5: {"n": 10},
        6: {"n": 11}, 7: {"n": 12}, 8: {"n": 14}, 9: {"n": 15}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["n"])
        self.task_type = "pairs"
        self.augment = augment
        self.seq = "".join(random.choice(_ALPHABET) for _ in range(self.length))
        self.answer = nussinov(self.seq)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, seq=self.seq)))

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
