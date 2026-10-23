"""SquarefreeRowTask — бесквадратные числа от 1 до границы.

Число бесквадратно, если его не делит квадрат простого. Единица бесквадратна.
Граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def squarefree_flags(limit: int) -> List[int]:
    marks = [1] * (limit + 1)
    marks[0] = 0
    prime = 2
    while prime * prime <= limit:
        square = prime * prime
        for multiple in range(square, limit + 1, square):
            marks[multiple] = 0
        prime += 1
    return marks


class SquarefreeRowTask(BaseMathTask):
    TASK_TYPE = "squarefree_row"
    TASK_TYPES = ["count", "free"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 8}, 2: {"n": 10}, 3: {"n": 12}, 4: {"n": 16},
        5: {"n": 20}, 6: {"n": 24}, 7: {"n": 28}, 8: {"n": 32},
        9: {"n": 36}, 10: {"n": 40},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.marks = squarefree_flags(self.n)
        self.count = sum(self.marks[1:])
        self.k = random.randint(1, self.n)
        self.free = self.marks[self.k]
        self.answer = self.count if self.task_type == "count" else self.free
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=number, free=self.marks[number])
            for number in range(1, self.n + 1)
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
