"""SpringSeriesTask — последовательные пружины под одной силой.

Число пружин растёт с уровнем. Жёсткость делит силу, поэтому каждое удлинение целое.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class SpringSeriesTask(BaseMathTask):
    TASK_TYPE = "spring_series"
    TASK_TYPES = ["extension"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "f": 6, "k": 6}, 2: {"n": 2, "f": 8, "k": 8},
        3: {"n": 3, "f": 12, "k": 8}, 4: {"n": 3, "f": 12, "k": 10},
        5: {"n": 4, "f": 18, "k": 12}, 6: {"n": 5, "f": 24, "k": 12},
        7: {"n": 6, "f": 30, "k": 15}, 8: {"n": 7, "f": 36, "k": 16},
        9: {"n": 8, "f": 48, "k": 18}, 10: {"n": 10, "f": 60, "k": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "extension"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.force = random.randint(1, int(p["f"]))
        kmax = int(p["k"])
        divisors = [item for item in range(1, kmax + 1) if self.force % item == 0] or [1]
        self.stiffness: List[int] = [random.choice(divisors) for _ in range(self.n)]
        self.extensions = [self.force // item for item in self.stiffness]
        self.total = sum(self.extensions)
        self.answer = self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [texts.t("s1", language, i=i, k=item) for i, item in enumerate(self.stiffness, 1)]
        return texts.t("s0", language, n=self.n, force=self.force, listing=" ".join(parts))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, force=self.force, k=k, x=x)
            for i, (k, x) in enumerate(zip(self.stiffness, self.extensions), 1)
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
