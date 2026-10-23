"""NaiveFindTask — наивный поиск образца и число сравнений символов.

На каждом выравнивании символы сравниваются, пока не кончится образец или не будет различия.
Считаются все выравнивания. Длина ряда выравниваний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def naive_scan(text: str, pattern: str) -> Tuple[int, int, List[int]]:
    checks = 0
    found = 0
    per_align = []
    last = len(text) - len(pattern) + 1
    for start in range(last):
        used = 0
        for offset, symbol in enumerate(pattern):
            used += 1
            checks += 1
            if text[start + offset] != symbol:
                break
        else:
            if found == 0:
                found = start + 1
        per_align.append(used)
    return found, checks, per_align


class NaiveFindTask(BaseMathTask):
    TASK_TYPE = "naive_find"
    TASK_TYPES = ["index", "checks"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 2}, 2: {"n": 2, "m": 2}, 3: {"n": 3, "m": 2},
        4: {"n": 4, "m": 2}, 5: {"n": 5, "m": 3}, 6: {"n": 6, "m": 3},
        7: {"n": 8, "m": 3}, 8: {"n": 9, "m": 3}, 9: {"n": 10, "m": 4},
        10: {"n": 12, "m": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.m = max(2, int(p["m"]))
        self.text = "".join(str(random.randint(0, 1)) for _ in range(self.n + self.m - 1))
        self.pattern = "".join(str(random.randint(0, 1)) for _ in range(self.m))
        self.index, self.checks, self.used = naive_scan(self.text, self.pattern)
        self.answer = self.index if self.task_type == "index" else self.checks
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "index" else "s1"
        return texts.t(
            key, language, text=self.text, pattern=self.pattern, n=self.n, m=self.m,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, used=used)
            for index, used in enumerate(self.used, 1)
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
