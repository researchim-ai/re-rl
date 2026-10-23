"""MassShiftTask — килограмм за шагом переносят с одной стороны блока на другую.

Разность масс уменьшается на 2. Ноль разности — равновесие.
Число переносов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def shift_trace(left: int, right: int, steps: int) -> List[Tuple[int, int, int, int]]:
    even = 0
    trace = []
    for index in range(1, steps + 1):
        if left > 0:
            left -= 1
            right += 1
        pull = left - right
        if even == 0 and pull == 0:
            even = index
        trace.append((left, right, pull, even))
    return trace


class MassShiftTask(BaseMathTask):
    TASK_TYPE = "mass_shift"
    TASK_TYPES = ["pull", "even"]

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
        self.right0 = random.randint(1, 5)
        self.left0 = self.right0 + 2 * random.randint(0, self.n)
        self.trace = shift_trace(self.left0, self.right0, self.n)
        _, _, self.pull, self.even = self.trace[-1]
        self.answer = self.pull if self.task_type == "pull" else self.even
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "pull" else "s1"
        return texts.t(key, language, left=self.left0, right=self.right0, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, pull=pull, even=even)
            for index, (left, right, pull, even) in enumerate(self.trace, 1)
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
