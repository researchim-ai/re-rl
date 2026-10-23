"""PalindromeRadiusTask — радиусы нечётных палиндромов вокруг каждой буквы.

Радиус — сколько пар одинаковых символов стоит по обе стороны от центра.
Длина строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def palindrome_radii(symbols: str) -> List[int]:
    radii = []
    size = len(symbols)
    for center in range(size):
        radius = 0
        while (
            center - radius - 1 >= 0
            and center + radius + 1 < size
            and symbols[center - radius - 1] == symbols[center + radius + 1]
        ):
            radius += 1
        radii.append(radius)
    return radii


class PalindromeRadiusTask(BaseMathTask):
    TASK_TYPE = "palindrome_radius"
    TASK_TYPES = ["longest", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.symbols = "".join(str(random.randint(0, 1)) for _ in range(self.n))
        self.radii = palindrome_radii(self.symbols)
        self.longest = 2 * max(self.radii) + 1
        self.k = random.randint(1, self.n)
        self.at_k = self.radii[self.k - 1]
        self.answer = self.longest if self.task_type == "longest" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(self.symbols)
        key = "s0" if self.task_type == "longest" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, radius=radius)
            for index, radius in enumerate(self.radii, 1)
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
