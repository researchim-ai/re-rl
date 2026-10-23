"""StablePlaceTask — итоговые места после устойчивой сортировки.

Сначала сравнивается значение, при равенстве сохраняется прежний порядок.
Длина списка растёт с уровнем, сортировка индексов идёт за O(n log n).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stable_order(values: Sequence[int]) -> Tuple[List[int], List[int]]:
    order = sorted(range(len(values)), key=lambda index: (values[index], index))
    place = [0] * len(values)
    for position, index in enumerate(order):
        place[index] = position + 1
    return place, order


class StablePlaceTask(BaseMathTask):
    TASK_TYPE = "stable_place"
    TASK_TYPES = ["place", "who"]

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
        self.values = [random.randint(1, 4) for _ in range(self.n)]
        self.place, self.order = stable_order(self.values)
        self.k = random.randint(1, self.n)
        self.who = self.order[self.k - 1] + 1
        self.answer = self.place[self.k - 1] if self.task_type == "place" else self.who
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=position, who=index + 1, value=self.values[index])
            for position, index in enumerate(self.order, 1)
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
