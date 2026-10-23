"""WindowDistinctTask — число различных значений в каждом окне.

Окна длины width идут слева направо с шагом 1. Подсчёт одного окна линейный,
а окон немного, поэтому генерация остаётся дешёвой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def distinct_windows(values: Sequence[int], width: int) -> List[int]:
    counts = []
    last = len(values) - width + 1
    for start in range(last):
        counts.append(len(set(values[start:start + width])))
    return counts


class WindowDistinctTask(BaseMathTask):
    TASK_TYPE = "window_distinct"
    TASK_TYPES = ["total", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "w": 2}, 2: {"n": 2, "w": 2}, 3: {"n": 3, "w": 2},
        4: {"n": 4, "w": 3}, 5: {"n": 5, "w": 3}, 6: {"n": 6, "w": 3},
        7: {"n": 8, "w": 4}, 8: {"n": 9, "w": 4}, 9: {"n": 10, "w": 4},
        10: {"n": 12, "w": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.width = max(2, int(p["w"]))
        self.values = [random.randint(0, 3) for _ in range(self.n + self.width - 1)]
        self.counts = distinct_windows(self.values, self.width)
        self.total = sum(self.counts)
        self.k = random.randint(1, self.n)
        self.at_k = self.counts[self.k - 1]
        self.answer = self.total if self.task_type == "total" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, width=self.width, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, count=count)
            for index, count in enumerate(self.counts, 1)
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
