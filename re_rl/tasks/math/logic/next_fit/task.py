"""NextFitTask — упаковка в ящики по правилу следующего.

Предмет идёт в текущий ящик, если влезает. Иначе открывается новый.
Число предметов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def next_fit(items: Sequence[int], capacity: int) -> List[Tuple[int, int]]:
    bins = 1
    used = 0
    trace = []
    for item in items:
        if used + item > capacity:
            bins += 1
            used = 0
        used += item
        trace.append((bins, used))
    return trace


class NextFitTask(BaseMathTask):
    TASK_TYPE = "next_fit"
    TASK_TYPES = ["bins", "fill"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "cap": 5}, 2: {"n": 3, "cap": 5}, 3: {"n": 4, "cap": 5},
        4: {"n": 5, "cap": 6}, 5: {"n": 6, "cap": 6}, 6: {"n": 8, "cap": 6},
        7: {"n": 9, "cap": 7}, 8: {"n": 10, "cap": 7}, 9: {"n": 12, "cap": 8},
        10: {"n": 14, "cap": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.capacity = max(1, int(p["cap"]))
        self.items = [random.randint(1, self.capacity) for _ in range(self.n)]
        self.trace = next_fit(self.items, self.capacity)
        self.bins, self.fill = self.trace[-1]
        self.answer = self.bins if self.task_type == "bins" else self.fill
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.items)
        key = "s0" if self.task_type == "bins" else "s1"
        return texts.t(key, language, n=self.n, capacity=self.capacity, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bins=bins, fill=fill)
            for index, (bins, fill) in enumerate(self.trace, 1)
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
