"""SgdOnlineTask — пошаговый градиентный спуск по одному примеру.

Модель y = w*x. На примере остаток считается до обновления веса.
Число примеров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def sgd_trace(start: int, points: Sequence[Pair]) -> List[Tuple[int, int, int]]:
    weight = start
    loss = 0
    trace = []
    for x, y in points:
        residual = weight * x - y
        loss += residual * residual
        weight -= x * residual
        trace.append((residual, weight, loss))
    return trace


class SgdOnlineTask(BaseMathTask):
    TASK_TYPE = "sgd_online"
    TASK_TYPES = ["weight", "loss"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 2}, 2: {"n": 3, "m": 2}, 3: {"n": 4, "m": 2},
        4: {"n": 5, "m": 3}, 5: {"n": 6, "m": 3}, 6: {"n": 7, "m": 3},
        7: {"n": 8, "m": 3}, 8: {"n": 9, "m": 3}, 9: {"n": 10, "m": 4},
        10: {"n": 12, "m": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.start = random.randint(-limit, limit)
        self.points = [
            (random.choice([-limit, -1, 1, limit]), random.randint(-limit, limit))
            for _ in range(self.n)
        ]
        self.trace = sgd_trace(self.start, self.points)
        _, self.weight, self.loss = self.trace[-1]
        self.answer = self.weight if self.task_type == "weight" else self.loss
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{x}, {y}" for x, y in self.points)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, x=x, y=y, residual=residual, weight=weight, loss=loss)
            for index, ((x, y), (residual, weight, loss)) in enumerate(zip(self.points, self.trace), 1)
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
