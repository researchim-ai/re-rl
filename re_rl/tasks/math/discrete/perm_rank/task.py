"""PermRankTask — ранг перестановки в факториальной системе.

Цифра кода — сколько ещё не вычеркнутых чисел меньше текущего.
Ранг тождественной перестановки равен 0. Длина растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def factorial_rank(perm: Sequence[int]) -> Tuple[List[int], List[int]]:
    remaining = list(range(1, len(perm) + 1))
    size = len(perm)
    weights = [1] * size
    for index in range(size - 2, -1, -1):
        weights[index] = weights[index + 1] * (size - 1 - index)
    digits = []
    running = []
    rank = 0
    for index, value in enumerate(perm):
        digit = remaining.index(value)
        remaining.pop(digit)
        digits.append(digit)
        rank += digit * weights[index]
        running.append(rank)
    return digits, running


class PermRankTask(BaseMathTask):
    TASK_TYPE = "perm_rank"
    TASK_TYPES = ["rank", "digit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.perm = list(range(1, self.n + 1))
        random.shuffle(self.perm)
        self.digits, self.running = factorial_rank(self.perm)
        self.k = random.randint(1, self.n)
        self.rank = self.running[-1]
        self.digit = self.digits[self.k - 1]
        self.answer = self.rank if self.task_type == "rank" else self.digit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(value) for value in self.perm)
        key = "s0" if self.task_type == "rank" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, digit=digit, rank=rank)
            for index, (value, digit, rank) in enumerate(zip(self.perm, self.digits, self.running), 1)
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
