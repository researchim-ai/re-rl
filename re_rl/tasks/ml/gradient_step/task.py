"""GradientStepTask — один шаг градиентного спуска для одномерной регрессии.

Модель y = w*x, функция потерь L = (1/2) * sum (w*x_i - y_i)^2,
градиент g = sum (w*x_i - y_i)*x_i, шаг w := w - lr * g при lr = 1.
Все величины целые.

Подтипы: ``gradient`` (сам градиент) и ``weight`` (вес после шага).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def gradient(w: int, points: List[Pair]) -> int:
    return sum((w * x - y) * x for x, y in points)


class GradientStepTask(BaseMathTask):
    TASK_TYPE = "gradient_step"
    TASK_TYPES = ["gradient", "weight"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 1, "coord": 2}, 2: {"n": 2, "coord": 2}, 3: {"n": 2, "coord": 2},
        4: {"n": 2, "coord": 3}, 5: {"n": 3, "coord": 2}, 6: {"n": 3, "coord": 3},
        7: {"n": 3, "coord": 3}, 8: {"n": 4, "coord": 3}, 9: {"n": 4, "coord": 3},
        10: {"n": 4, "coord": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.coord = int(p["coord"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.points = [(random.randint(-self.coord, self.coord), random.randint(-self.coord, self.coord))
                       for _ in range(self.n)]
        if all(x == 0 for x, _ in self.points):
            self.points[0] = (1, self.points[0][1])
        self.w = random.randint(-2, 2)
        self.grad = gradient(self.w, self.points)
        self.w_new = self.w - self.grad

    def _pts(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self.points)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        data = ((texts.t('s1', language, v0=self._pts(), w=self.w)))
        if self.task_type == "gradient":
            ask = ((texts.t('s3', language)))
        else:
            ask = ((texts.t('s4', language)))
        return f"{rule} {data} {ask}"

    def solve(self):
        from re_rl.tasks.ml.detailed_solvers import solve_detailed
        solve_detailed(self)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        truth = self.grad if self.task_type == "gradient" else self.w_new
        return U.verify_int(prediction, int(truth))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
