"""BounceHeightsTask — высоты после отскоков с коэффициентом 1/2.

Стартовая высота делится на 2^n, поэтому после каждого удара высота целая.
Число отскоков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BounceHeightsTask(BaseMathTask):
    TASK_TYPE = "bounce_heights"
    TASK_TYPES = ["final", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 5}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 6}, 8: {"n": 7, "m": 6}, 9: {"n": 8, "m": 6},
        10: {"n": 10, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.unit = random.randint(1, int(p["m"]))
        self.start = self.unit * 2 ** self.n
        self.heights: List[int] = []
        height = self.start
        for _ in range(self.n):
            height //= 2
            self.heights.append(height)
        self.k = random.randint(1, self.n)
        self.final = self.heights[-1]
        self.at_k = self.heights[self.k - 1]
        self.answer = self.final if self.task_type == "final" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, before=self.start // 2 ** (i - 1), height=height)
            for i, height in enumerate(self.heights, 1)
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
