"""CandyRowTask — конфеты по рейтингу соседей.

Сначала у каждого одна конфета. Слева направо и справа налево рейтинг выше соседнего
добавляет ещё одну относительно этого соседа. Число детей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def candy_passes(ratings: Sequence[int]) -> Tuple[List[int], List[int]]:
    count = len(ratings)
    left = [1] * count
    for index in range(1, count):
        if ratings[index] > ratings[index - 1]:
            left[index] = left[index - 1] + 1
    final = left[:]
    for index in range(count - 2, -1, -1):
        if ratings[index] > ratings[index + 1]:
            need = final[index + 1] + 1
            if need > final[index]:
                final[index] = need
    return left, final


class CandyRowTask(BaseMathTask):
    TASK_TYPE = "candy_row"
    TASK_TYPES = ["total", "at_k"]

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
        self.ratings = [random.randint(1, 5) for _ in range(self.n)]
        self.left, self.final = candy_passes(self.ratings)
        self.total = sum(self.final)
        self.k = random.randint(1, self.n)
        self.at_k = self.final[self.k - 1]
        self.answer = self.total if self.task_type == "total" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.ratings)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, rating=rating, candies=candies)
            for index, (rating, candies) in enumerate(zip(self.ratings, self.left), 1)
        ]
        steps.extend(
            texts.t("s3", self.language, i=index, candies=candies)
            for index, candies in enumerate(self.final, 1)
        )
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
