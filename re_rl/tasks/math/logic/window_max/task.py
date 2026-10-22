"""WindowMaxTask — максимумы скользящего окна.

Число окон растёт с уровнем. Ширина окна задаётся отдельно от длины массива.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class WindowMaxTask(BaseMathTask):
    TASK_TYPE = "window_max"
    TASK_TYPES = ["total", "changes"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "k": 2, "v": 4}, 2: {"n": 4, "k": 2, "v": 5},
        3: {"n": 5, "k": 2, "v": 5}, 4: {"n": 6, "k": 2, "v": 6},
        5: {"n": 8, "k": 3, "v": 6}, 6: {"n": 9, "k": 3, "v": 8},
        7: {"n": 11, "k": 3, "v": 8}, 8: {"n": 12, "k": 4, "v": 9},
        9: {"n": 14, "k": 4, "v": 9}, 10: {"n": 16, "k": 3, "v": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.length = max(2, int(p["n"]))
        self.k = max(1, min(int(p["k"]), self.length))
        limit = int(p["v"])
        self.values = [random.randint(-limit, limit) for _ in range(self.length)]
        self.maxima = [
            max(self.values[start:start + self.k])
            for start in range(self.length - self.k + 1)
        ]
        self.n = len(self.maxima)
        self.total = sum(self.maxima)
        self.changes = sum(1 for left, right in zip(self.maxima, self.maxima[1:]) if left != right)
        self.answer = self.total if self.task_type == "total" else self.changes
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, length=self.length, k=self.k, listing=listing)

    def solve(self):
        steps = []
        for index, value in enumerate(self.maxima, 1):
            window = ", ".join(str(item) for item in self.values[index - 1:index - 1 + self.k])
            steps.append(texts.t("s2", self.language, i=index, window=window, value=value))
        steps.append(texts.t("s3", self.language, total=self.total, changes=self.changes))
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
