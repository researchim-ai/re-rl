"""PartCountTask — разбиение списка относительно порога.

Меньшие порога идут влево, равные считаются отдельно, большие не входят ни в левую часть, ни в равные.
Число чисел растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def part_trace(values: Sequence[int], pivot: int) -> List[Tuple[int, int]]:
    left = 0
    equal = 0
    trace = []
    for value in values:
        if value < pivot:
            left += 1
        elif value == pivot:
            equal += 1
        trace.append((left, equal))
    return trace


class PartCountTask(BaseMathTask):
    TASK_TYPE = "part_count"
    TASK_TYPES = ["left", "equal"]

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
        self.pivot = random.randint(1, 6)
        self.values = [random.randint(0, 8) for _ in range(self.n)]
        self.trace = part_trace(self.values, self.pivot)
        self.left = self.trace[-1][0]
        self.equal = self.trace[-1][1]
        self.answer = self.left if self.task_type == "left" else self.equal
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(key, language, n=self.n, pivot=self.pivot, values=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, left=left, equal=equal)
            for index, (value, (left, equal)) in enumerate(zip(self.values, self.trace), 1)
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
