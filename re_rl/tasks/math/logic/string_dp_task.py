"""Классические строковые ДП: расстояние Левенштейна и наибольшая общая
подпоследовательность (длина)."""

import random
import string
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class EditDistanceTask(BaseMathTask):
    TASK_TYPE = "edit_distance"
    TASK_TYPES = ["edit_distance", "lcs"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 3, "alpha": 2}, 2: {"L": 4, "alpha": 3}, 3: {"L": 5, "alpha": 3},
        4: {"L": 6, "alpha": 3}, 5: {"L": 7, "alpha": 4}, 6: {"L": 8, "alpha": 4},
        7: {"L": 9, "alpha": 4}, 8: {"L": 10, "alpha": 5}, 9: {"L": 12, "alpha": 5},
        10: {"L": 14, "alpha": 6},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L = int(p["L"])
        self.alpha = int(p["alpha"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        letters = string.ascii_lowercase[:self.alpha]
        self.s1 = "".join(random.choice(letters) for _ in range(self.L + random.randint(-1, 1)))
        self.s2 = "".join(random.choice(letters) for _ in range(self.L + random.randint(-1, 1)))
        self._answer = self._lev() if self.subtype == "edit_distance" else self._lcs()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _lev(self):
        a, b = self.s1, self.s2
        dp = list(range(len(b) + 1))
        for i in range(1, len(a) + 1):
            prev = dp[0]
            dp[0] = i
            for j in range(1, len(b) + 1):
                cur = dp[j]
                dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
                prev = cur
        return dp[len(b)]

    def _lcs(self):
        a, b = self.s1, self.s2
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
        return dp[len(a)][len(b)]

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "edit_distance":
            return ((f"Найдите расстояние Левенштейна (минимальное число вставок, удалений и замен одного "
                     f"символа) между строками «{self.s1}» и «{self.s2}».") if ru else
                    (f"Find the Levenshtein distance (minimum number of single-character insertions, "
                     f"deletions, substitutions) between '{self.s1}' and '{self.s2}'."))
        return ((f"Найдите длину наибольшей общей подпоследовательности строк «{self.s1}» и «{self.s2}» "
                 f"(символы идут в том же порядке, но не обязательно подряд).") if ru else
                (f"Find the length of the longest common subsequence of '{self.s1}' and '{self.s2}' "
                 f"(characters in the same order, not necessarily contiguous)."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Заполняем таблицу динамического программирования по символам обеих строк." if ru else
             "Fill the dynamic-programming table over both strings' characters."),
            (f"Ответ = {self._answer}." if ru else f"Answer = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
