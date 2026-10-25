"""HammingStepTask — число различающихся битов у соседних чисел.

Числа от 0 до 15. Расстояние — сколько битов различно. Считаются только соседние пары.
Число пар растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ham_trace(values: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    peak = 0
    trace = []
    for left, right in zip(values, values[1:]):
        dist = (left ^ right).bit_count()
        total += dist
        peak = max(peak, dist)
        trace.append((dist, total, peak))
    return trace


class HammingStepTask(BaseMathTask):
    TASK_TYPE = "hamming_step"
    TASK_TYPES = ["total", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values = [random.randint(0, 15) for _ in range(self.n + 1)]
        self.trace = ham_trace(self.values)
        self.total = self.trace[-1][1]
        self.peak = self.trace[-1][2]
        self.answer = self.total if self.task_type == "total" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, values=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, dist=dist, total=total, peak=peak)
            for index, (left, right, (dist, total, peak)) in enumerate(
                zip(self.values, self.values[1:], self.trace), 1
            )
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
