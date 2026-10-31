"""MaxSubarrayTask — наибольшая сумма непустого непрерывного фрагмента (Кадане)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def kadane(values: List[int]) -> int:
    best = current = values[0]
    for value in values[1:]:
        current = value if value > current + value else current + value
        if current > best:
            best = current
    return best


class MaxSubarrayTask(BaseMathTask):
    TASK_TYPE = "max_subarray"
    TASK_TYPES = ["sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "mag": 5}, 2: {"n": 5, "mag": 6}, 3: {"n": 6, "mag": 6},
        4: {"n": 7, "mag": 8}, 5: {"n": 8, "mag": 8}, 6: {"n": 9, "mag": 9},
        7: {"n": 10, "mag": 9}, 8: {"n": 12, "mag": 10}, 9: {"n": 14, "mag": 12},
        10: {"n": 16, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "sum"
        self.augment = augment
        self.values = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        if all(v <= 0 for v in self.values):
            self.values[random.randrange(self.n)] = random.randint(1, self.mag)
        self.answer = kadane(self.values)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = " ".join(map(str, self.values))
        return ((texts.t('s0', language, data=data)))

    def solve(self):
        from re_rl.tasks.math.algorithm_traces.solvers import solve_detailed
        solve_detailed(self)

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
