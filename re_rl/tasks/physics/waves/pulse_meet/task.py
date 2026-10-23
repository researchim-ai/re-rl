"""PulseMeetTask — два импульса на струне идут навстречу.

За такт левый сдвигается вправо на 1, правый влево на 1. В одной клетке высоты складываются.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pulse_trace(left_h: int, right_h: int, gap: int, ticks: int) -> List[Tuple[int, int, int, int, int]]:
    left = 0
    right = gap
    meet = 0
    place = 0
    peak = 0
    trace = []
    for index in range(1, ticks + 1):
        left += 1
        right -= 1
        height = left_h + right_h if left == right else max(left_h, right_h)
        if height > peak:
            peak = height
        if meet == 0 and left == right:
            meet = index
            place = left
        trace.append((left, right, peak, meet, place))
    return trace


class PulseMeetTask(BaseMathTask):
    TASK_TYPE = "pulse_meet"
    TASK_TYPES = ["peak", "place"]

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
        self.left_h = random.randint(1, 4)
        self.right_h = random.randint(1, 4)
        self.gap = 2 * random.randint(1, max(1, self.n // 2))
        self.trace = pulse_trace(self.left_h, self.right_h, self.gap, self.n)
        _, _, self.peak, _, self.place = self.trace[-1]
        self.answer = self.peak if self.task_type == "peak" else self.place
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "peak" else "s1"
        return texts.t(
            key, language, n=self.n, left=self.left_h, right=self.right_h, gap=self.gap,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, peak=peak, meet=meet, place=place)
            for index, (left, right, peak, meet, place) in enumerate(self.trace, 1)
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
