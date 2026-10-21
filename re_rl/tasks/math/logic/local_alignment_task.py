"""LocalAlignmentTask — вес локального выравнивания Смита–Уотермана.

Совпадение даёт +1, несовпадение и дырка дают -1.
Пустое выравнивание имеет вес 0, поэтому ответ не бывает отрицательным.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ALPHABET = "acgt"


def local_alignment(left: str, right: str, match: int = 1, mismatch: int = -1, gap: int = -1) -> int:
    n, m = len(left), len(right)
    best = 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diagonal = dp[i - 1][j - 1] + (match if left[i - 1] == right[j - 1] else mismatch)
            dp[i][j] = max(0, diagonal, dp[i - 1][j] + gap, dp[i][j - 1] + gap)
            if dp[i][j] > best:
                best = dp[i][j]
    return best


class LocalAlignmentTask(BaseMathTask):
    TASK_TYPE = "local_alignment"
    TASK_TYPES = ["score"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 7},
        6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10}, 9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["n"])
        self.task_type = "score"
        self.augment = augment
        self.left = "".join(random.choice(_ALPHABET) for _ in range(self.length))
        self.right = "".join(random.choice(_ALPHABET) for _ in range(random.randint(3, self.length)))
        self.answer = local_alignment(self.left, self.right)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Локальное выравнивание строк {self.left} и {self.right}. "
                 f"Совпадение даёт +1, несовпадение даёт -1, дырка даёт -1. "
                 f"Можно выровнять пустые куски, их вес 0. Найдите наибольший вес.") if ru else
                (f"Local alignment of {self.left} and {self.right}. "
                 f"A match scores +1, a mismatch scores -1, and a gap scores -1. "
                 f"Empty pieces may be aligned and score 0. Find the best score."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Вес локального выравнивания равен {self.answer}.") if ru else
                (f"The local alignment score is {self.answer}."))
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
