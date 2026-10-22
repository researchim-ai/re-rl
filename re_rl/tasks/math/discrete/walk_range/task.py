"""WalkRangeTask — блуждание шагами +1 и -1.

Число шагов растёт с уровнем. Итоговая точка — это сумма, а наименьшая высота требует просмотра всего пути.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class WalkRangeTask(BaseMathTask):
    TASK_TYPE = "walk_range"
    TASK_TYPES = ["final", "lowest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.deltas: List[int] = [random.choice((-1, 1)) for _ in range(self.n)]
        height = 0
        self.heights: List[int] = []
        for delta in self.deltas:
            height += delta
            self.heights.append(height)
        self.final = height
        self.lowest = min([0] + self.heights)
        self.answer = self.final if self.task_type == "final" else self.lowest
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(f"{item:+d}" for item in self.deltas)
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, delta=f"{delta:+d}", height=height)
            for i, (delta, height) in enumerate(zip(self.deltas, self.heights), 1)
        ]
        steps.append(texts.t("s3", self.language, final=self.final, lowest=self.lowest))
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
