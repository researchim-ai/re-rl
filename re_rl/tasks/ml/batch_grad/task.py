"""BatchGradTask — один шаг на пакет из двух примеров.

Градиент пакета складывается до изменения веса. Модель y = w*x.
Число пакетов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]
Batch = Tuple[Pair, Pair]


def batch_trace(start: int, batches: Sequence[Batch]) -> List[Tuple[int, int]]:
    weight = start
    trace = []
    for (x1, y1), (x2, y2) in batches:
        gradient = (weight * x1 - y1) * x1 + (weight * x2 - y2) * x2
        weight -= gradient
        trace.append((gradient, weight))
    return trace


class BatchGradTask(BaseMathTask):
    TASK_TYPE = "batch_grad"
    TASK_TYPES = ["weight", "grad"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.start = random.randint(-2, 2)
        self.batches = []
        for _ in range(self.n):
            self.batches.append((
                (random.randint(-2, 2), random.randint(-3, 3)),
                (random.randint(-2, 2), random.randint(-3, 3)),
            ))
        self.trace = batch_trace(self.start, self.batches)
        self.grad, self.weight = self.trace[-1]
        self.answer = self.weight if self.task_type == "weight" else self.grad
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{x1} {y1}, {x2} {y2}" for (x1, y1), (x2, y2) in self.batches
        )
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, grad=grad, weight=weight)
            for index, (grad, weight) in enumerate(self.trace, 1)
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
