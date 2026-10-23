"""BallotWalkTask — путь из шагов вверх и вниз.

Шаг 1 поднимает сумму на 1, шаг 0 опускает на 1. Старт с нуля.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ballot_trace(steps: Sequence[int]) -> List[Tuple[int, int, int]]:
    height = 0
    low = 0
    fall = 0
    trace = []
    for index, step in enumerate(steps, 1):
        height += 1 if step else -1
        if height < low:
            low = height
        if fall == 0 and height < 0:
            fall = index
        trace.append((height, low, fall))
    return trace


class BallotWalkTask(BaseMathTask):
    TASK_TYPE = "ballot_walk"
    TASK_TYPES = ["low", "fall"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.steps = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = ballot_trace(self.steps)
        _, self.low, self.fall = self.trace[-1]
        self.answer = self.low if self.task_type == "low" else self.fall
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(step) for step in self.steps)
        key = "s0" if self.task_type == "low" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, height=height, low=low, fall=fall)
            for index, (height, low, fall) in enumerate(self.trace, 1)
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
