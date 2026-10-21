"""MajorityTask — элемент, который встречается строго больше n/2 раз.

Такой элемент в выборке ровно один.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def majority(values: List[int]) -> int:
    counts: Dict[int, int] = {}
    need = len(values) // 2 + 1
    for value in values:
        counts[value] = counts.get(value, 0) + 1
        if counts[value] >= need:
            return value
    raise RuntimeError("строгого большинства нет")


class MajorityTask(BaseMathTask):
    TASK_TYPE = "majority_element"
    TASK_TYPES = ["element"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 5}, 2: {"n": 5, "mag": 6}, 3: {"n": 5, "mag": 8},
        4: {"n": 7, "mag": 8}, 5: {"n": 7, "mag": 10}, 6: {"n": 9, "mag": 10},
        7: {"n": 9, "mag": 12}, 8: {"n": 11, "mag": 12}, 9: {"n": 13, "mag": 15},
        10: {"n": 15, "mag": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "element"
        self.augment = augment
        self.answer = random.randint(0, self.mag)
        need = self.n // 2 + 1
        others = [random.randint(0, self.mag) for _ in range(self.n - need)]
        self.values = [self.answer] * need + others
        random.shuffle(self.values)
        if majority(self.values) != self.answer:
            raise RuntimeError("большинство потерялось при генерации")
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.values))
        return ((f"В массиве {data} один элемент встречается строго больше половины раз. Найдите его.")
                if ru else
                (f"In the array {data} one element occurs strictly more than half the time. Find it."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Элемент большинства — {self.answer}.") if ru else
             (f"The majority element is {self.answer}.")),
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
