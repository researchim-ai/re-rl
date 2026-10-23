"""SumKindsTask — число различных сумм подмножеств.

Пустое подмножество даёт 0. Каждое новое положительное число расширяет множество сумм.
Длина набора растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def subset_growth(numbers: Sequence[int]) -> Tuple[List[int], List[Set[int]]]:
    sums = {0}
    counts = []
    history = []
    for value in numbers:
        sums = sums | {item + value for item in sums}
        counts.append(len(sums))
        history.append(set(sums))
    return counts, history


class SumKindsTask(BaseMathTask):
    TASK_TYPE = "sum_kinds"
    TASK_TYPES = ["kinds", "hit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 5}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 6},
        7: {"n": 6, "m": 6}, 8: {"n": 7, "m": 7}, 9: {"n": 8, "m": 8},
        10: {"n": 10, "m": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.numbers = [random.randint(1, limit) for _ in range(self.n)]
        self.counts, self.history = subset_growth(self.numbers)
        self.sums = self.history[-1]
        self.kinds = self.counts[-1]
        if random.randint(0, 1) == 0:
            self.target = random.choice(tuple(self.sums))
        else:
            self.target = sum(self.numbers) + 1
        self.flags = [int(self.target in state) for state in self.history]
        self.hit = self.flags[-1]
        self.answer = self.kinds if self.task_type == "kinds" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.numbers)
        if self.task_type == "kinds":
            return texts.t("s0", language, n=self.n, listing=listing)
        return texts.t("s1", language, n=self.n, listing=listing, target=self.target)

    def solve(self):
        steps = []
        for index, (value, kinds, flag) in enumerate(zip(self.numbers, self.counts, self.flags), 1):
            if self.task_type == "kinds":
                steps.append(texts.t("s2", self.language, i=index, value=value, kinds=kinds))
            else:
                steps.append(texts.t(
                    "s3", self.language, i=index, value=value, target=self.target, flag=flag,
                ))
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
