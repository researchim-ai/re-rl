"""LensStackTask — тонкие линзы, составленные вплотную.

Число линз растёт с уровнем. Суммарная оптическая сила равна сумме сил в диоптриях.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class LensStackTask(BaseMathTask):
    TASK_TYPE = "lens_stack"
    TASK_TYPES = ["power"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "d": 4}, 2: {"n": 2, "d": 5}, 3: {"n": 3, "d": 6},
        4: {"n": 3, "d": 6}, 5: {"n": 4, "d": 8}, 6: {"n": 5, "d": 8},
        7: {"n": 6, "d": 10}, 8: {"n": 7, "d": 10}, 9: {"n": 8, "d": 12},
        10: {"n": 10, "d": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "power"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["d"])
        choices = [item for item in range(-limit, limit + 1) if item != 0]
        self.powers: List[int] = [random.choice(choices) for _ in range(self.n)]
        self.total = sum(self.powers)
        self.answer = self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [texts.t("s1", language, i=i, power=item) for i, item in enumerate(self.powers, 1)]
        return texts.t("s0", language, n=self.n, listing=" ".join(parts))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, power=item)
            for i, item in enumerate(self.powers, 1)
        ]
        steps.append(texts.t("s3", self.language, total=self.total))
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
