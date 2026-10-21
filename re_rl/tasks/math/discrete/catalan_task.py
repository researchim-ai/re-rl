"""CatalanTask — числа Каталана.

C(0) = 1, C(n+1) = C(n) * (4n + 2) / (n + 2). Деление всегда нацело.

Подтипы:
- ``number``     — само число C(n);
- ``parentheses``— сколько правильных скобочных последовательностей из n пар (тоже C(n)).
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def catalan_sequence(n: int) -> List[int]:
    seq = [1]
    c = 1
    for k in range(n):
        nxt = c * (4 * k + 2)
        if nxt % (k + 2) != 0:
            raise RuntimeError("число Каталана не целое")
        c = nxt // (k + 2)
        seq.append(c)
    return seq


class CatalanTask(BaseMathTask):
    TASK_TYPE = "catalan"
    TASK_TYPES = ["number", "parentheses"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9}, 9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.seq = catalan_sequence(self.n)
        self.answer = self.seq[-1]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "number":
            return ((f"Числа Каталана: C(0) = 1 и C(n) = C(n-1) * (4n - 2) / (n + 1). "
                     f"Найдите C({self.n}).") if ru else
                    (f"Catalan numbers: C(0) = 1 and C(n) = C(n-1) * (4n - 2) / (n + 1). "
                     f"Find C({self.n})."))
        return ((f"Сколько существует правильных скобочных последовательностей из {self.n} пар скобок?")
                if ru else
                (f"How many valid parentheses strings are there with {self.n} pairs?"))

    def solve(self):
        ru = self.language == "ru"
        shown = ", ".join(f"C({i})={v}" for i, v in enumerate(self.seq))
        note = ("Это число Каталана." if self.task_type == "parentheses" else "По рекурренте.")
        note_en = ("This is the Catalan number." if self.task_type == "parentheses" else "By the recurrence.")
        self.solution_steps = [
            ((f"{note} {shown}.") if ru else f"{note_en} {shown}."),
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
