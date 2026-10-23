"""ZArrayTask — Z-функция строки.

Z[i] — длина наибольшего префикса, который начинается в позиции i.
Позиции с 1, Z первой позиции не спрашивается. Длина строки растёт с уровнем.
Сравнение наивное и при длине до 18 остаётся дешёвым.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def z_values(symbols: str) -> List[int]:
    size = len(symbols)
    values = [0] * size
    for start in range(1, size):
        while start + values[start] < size and symbols[values[start]] == symbols[start + values[start]]:
            values[start] += 1
    return values


class ZArrayTask(BaseMathTask):
    TASK_TYPE = "z_array"
    TASK_TYPES = ["at_k", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.symbols = "".join(str(random.randint(0, 1)) for _ in range(self.n))
        self.values = z_values(self.symbols)
        self.k = random.randint(2, self.n)
        self.at_k = self.values[self.k - 1]
        self.total = sum(self.values[1:])
        self.answer = self.at_k if self.task_type == "at_k" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(self.symbols)
        key = "s0" if self.task_type == "at_k" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.values[1:], 2)
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
