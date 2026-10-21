"""GradientStepTask — один шаг градиентного спуска для одномерной регрессии.

Модель y = w*x, функция потерь L = (1/2) * sum (w*x_i - y_i)^2,
градиент g = sum (w*x_i - y_i)*x_i, шаг w := w - lr * g при lr = 1.
Все величины целые.

Подтипы: ``gradient`` (сам градиент) и ``weight`` (вес после шага).
"""

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
        ru = language == "ru"
        rule = (("Модель y = w*x. Потеря L = (1/2) * sum (w*x_i - y_i)^2, "
                 "градиент g = sum (w*x_i - y_i)*x_i, шаг обучения lr = 1, "
                 "новый вес w_new = w - g.") if ru else
                ("Model y = w*x. Loss L = (1/2) * sum (w*x_i - y_i)^2, "
                 "gradient g = sum (w*x_i - y_i)*x_i, learning rate lr = 1, "
                 "new weight w_new = w - g."))
        data = ((f"Точки (x, y): {self._pts()}. Текущий вес w = {self.w}.") if ru else
                (f"Points (x, y): {self._pts()}. Current weight w = {self.w}."))
        if self.task_type == "gradient":
            ask = ("Чему равен градиент g?" if ru else "What is the gradient g?")
        else:
            ask = ("Чему равен вес после одного шага?" if ru else "What is the weight after one step?")
        return f"{rule} {data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        terms = " + ".join(f"({self.w}*{x} - {y})*{x}" for x, y in self.points)
        step = ((f"g = {terms} = {self.grad}. w_new = {self.w} - ({self.grad}) = {self.w_new}.")
                if ru else
                (f"g = {terms} = {self.grad}. w_new = {self.w} - ({self.grad}) = {self.w_new}."))
        ans = self.grad if self.task_type == "gradient" else self.w_new
        self.solution_steps = [step, (f"Ответ: {ans}." if ru else f"Answer: {ans}.")]
        self.final_answer = str(ans)

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
