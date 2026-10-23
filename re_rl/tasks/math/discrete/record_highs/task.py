"""RecordHighsTask — строгие рекорды слева направо.

Первое число всегда рекорд. Следующее становится рекордом, только если оно больше всех предыдущих.
Длина списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def record_trace(values: Sequence[int]) -> List[Tuple[int, int]]:
    best = values[0]
    records = 1
    trace = [(best, records)]
    for value in values[1:]:
        if value > best:
            best = value
            records += 1
        trace.append((best, records))
    return trace


class RecordHighsTask(BaseMathTask):
    TASK_TYPE = "record_highs"
    TASK_TYPES = ["peak", "records"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 5}, 3: {"n": 4, "m": 6},
        4: {"n": 5, "m": 6}, 5: {"n": 6, "m": 8}, 6: {"n": 8, "m": 8},
        7: {"n": 10, "m": 10}, 8: {"n": 12, "m": 10}, 9: {"n": 14, "m": 12},
        10: {"n": 16, "m": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.values = [random.randint(0, limit) for _ in range(self.n)]
        self.trace = record_trace(self.values)
        self.peak, self.records = self.trace[-1]
        self.answer = self.peak if self.task_type == "peak" else self.records
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "peak" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, peak=peak, records=records)
            for index, (value, (peak, records)) in enumerate(zip(self.values, self.trace), 1)
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
