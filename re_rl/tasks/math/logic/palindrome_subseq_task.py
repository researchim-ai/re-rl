"""PalindromeSubseqTask — длина самой длинной подпоследовательности-палиндрома.

Символы не обязаны стоять подряд, но их порядок сохраняется.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ALPHABET = "abcd"


def lps_length(text: str) -> int:
    n = len(text)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if text[i] == text[j]:
                dp[i][j] = 2 if length == 2 else dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]


class PalindromeSubseqTask(BaseMathTask):
    TASK_TYPE = "palindrome_subseq"
    TASK_TYPES = ["length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "alpha": 2}, 2: {"n": 5, "alpha": 2}, 3: {"n": 6, "alpha": 2},
        4: {"n": 6, "alpha": 3}, 5: {"n": 7, "alpha": 3}, 6: {"n": 8, "alpha": 3},
        7: {"n": 9, "alpha": 3}, 8: {"n": 10, "alpha": 4}, 9: {"n": 12, "alpha": 4},
        10: {"n": 14, "alpha": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["n"])
        self.alpha = int(p["alpha"])
        self.task_type = "length"
        self.augment = augment
        letters = _ALPHABET[:self.alpha]
        self.text = "".join(random.choice(letters) for _ in range(self.length))
        self.answer = lps_length(self.text)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Найдите длину самой длинной подпоследовательности-палиндрома в строке {self.text}. "
                 f"Символы не обязаны идти подряд, порядок сохраняется.") if ru else
                (f"Find the length of the longest palindromic subsequence of {self.text}. "
                 f"Characters need not be consecutive, and their order is preserved."))

    def solve(self):
        ru = self.language == "ru"
        step = ((f"Самая длинная палиндромная подпоследовательность имеет длину {self.answer}.") if ru else
                (f"The longest palindromic subsequence has length {self.answer}."))
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
