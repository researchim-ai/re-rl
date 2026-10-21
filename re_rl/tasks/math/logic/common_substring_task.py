"""CommonSubstringTask — длина наибольшей общей подстроки.

Подстрока идёт подряд, в отличие от подпоследовательности в edit_distance.
"""

import random
import string
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def longest_common_substring(a: str, b: str) -> int:
    best = 0
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0] * (len(b) + 1)
        for j, cb in enumerate(b):
            if ca == cb:
                cur[j + 1] = prev[j] + 1
                if cur[j + 1] > best:
                    best = cur[j + 1]
        prev = cur
    return best


class CommonSubstringTask(BaseMathTask):
    TASK_TYPE = "common_substring"
    TASK_TYPES = ["length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "alpha": 2}, 2: {"n": 5, "alpha": 2}, 3: {"n": 6, "alpha": 3},
        4: {"n": 6, "alpha": 3}, 5: {"n": 7, "alpha": 3}, 6: {"n": 8, "alpha": 3},
        7: {"n": 9, "alpha": 4}, 8: {"n": 10, "alpha": 4}, 9: {"n": 11, "alpha": 4},
        10: {"n": 12, "alpha": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.alpha = int(p["alpha"])
        self.task_type = "length"
        self.augment = augment
        letters = string.ascii_lowercase[:self.alpha]
        self.a = "".join(random.choice(letters) for _ in range(self.n))
        self.b = "".join(random.choice(letters) for _ in range(self.n + random.choice([-1, 0, 1])))
        # Подмешиваем общий кусок, чтобы ответ не всегда был 1.
        if self.n >= 4 and random.random() < 0.7:
            span = random.randint(2, max(2, self.n // 2))
            i = random.randint(0, len(self.a) - span)
            j = random.randint(0, len(self.b) - span)
            chunk = self.a[i:i + span]
            self.b = self.b[:j] + chunk + self.b[j + span:]
        self.answer = longest_common_substring(self.a, self.b)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Найдите длину наибольшей общей подстроки строк {self.a} и {self.b}. "
                 f"Подстрока — непрерывный фрагмент, не подпоследовательность.") if ru else
                (f"Find the length of the longest common substring of {self.a} and {self.b}. "
                 f"A substring is a contiguous fragment, not a subsequence."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Динамика по совпадающим соседним символам даёт длину {self.answer}.") if ru else
             (f"The DP on adjacent matches gives length {self.answer}.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
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
