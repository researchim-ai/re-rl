"""NecklaceCountTask — ожерелья из двух цветов при простом числе бусин.

Число ожерелий длины p равно (2^p + (p-1)*2) / p. Деление целое.
Простое p растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def necklace_trace(prime: int) -> List[int]:
    power = 1
    trace = []
    for _ in range(prime):
        power *= 2
        trace.append(power)
    assert (power + (prime - 1) * 2) % prime == 0
    return trace


class NecklaceCountTask(BaseMathTask):
    TASK_TYPE = "necklace_count"
    TASK_TYPES = ["count", "power"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 5}, 3: {"n": 7}, 4: {"n": 7},
        5: {"n": 11}, 6: {"n": 11}, 7: {"n": 13}, 8: {"n": 13},
        9: {"n": 17}, 10: {"n": 19},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = necklace_trace(self.n)
        self.power = self.trace[-1]
        self.count = (self.power + (self.n - 1) * 2) // self.n
        self.answer = self.count if self.task_type == "count" else self.power
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, power=power)
            for index, power in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, n=self.n, power=self.power, count=self.count))
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
