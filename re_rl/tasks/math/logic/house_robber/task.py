"""HouseRobberTask — максимум суммы домов, если нельзя брать соседние."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rob(values: List[int]) -> int:
    prev = current = 0
    for value in values:
        prev, current = current, max(current, prev + value)
    return current


class HouseRobberTask(BaseMathTask):
    TASK_TYPE = "house_robber"
    TASK_TYPES = ["max_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 6}, 2: {"n": 4, "mag": 8}, 3: {"n": 4, "mag": 9},
        4: {"n": 5, "mag": 10}, 5: {"n": 6, "mag": 12}, 6: {"n": 7, "mag": 12},
        7: {"n": 8, "mag": 15}, 8: {"n": 9, "mag": 15}, 9: {"n": 10, "mag": 18},
        10: {"n": 12, "mag": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = "max_sum"
        self.augment = augment
        self.values = [random.randint(1, self.mag) for _ in range(self.n)]
        self.answer = rob(self.values)
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
