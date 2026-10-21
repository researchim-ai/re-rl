"""Чтение графика функции (визуальная задача).

По изображению графика многочлена нужно определить:
- ``count_roots``  — сколько раз график пересекает ось X (число вещественных корней
  в окне);
- ``y_intercept``  — значение точки пересечения с осью Y (f(0)).

Условие НЕ содержит формулу функции — ответ считывается с картинки. Масштаб задаётся
степенью многочлена и диапазоном.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, Callable, ClassVar, Dict, List, Tuple

import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class FunctionPlotReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = texts.literal('literals.s5')
    TASK_TYPES = ["count_roots", "y_intercept"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 2, "R": 3}, 2: {"degree": 2, "R": 3}, 3: {"degree": 2, "R": 4},
        4: {"degree": 2, "R": 4}, 5: {"degree": 2, "R": 5}, 6: {"degree": 3, "R": 3},
        7: {"degree": 3, "R": 3}, 8: {"degree": 3, "R": 4}, 9: {"degree": 3, "R": 4},
        10: {"degree": 3, "R": 5},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.degree = int(p["degree"])
        self.R = int(p["R"])
        self.window = (-(self.R + 1), self.R + 1)
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        R = self.R
        self.a = random.choice([1, -1, 2, -2])
        if self.degree == 2:
            self.n_roots = random.choice([0, 1, 2])
            if self.n_roots == 2:
                r1, r2 = random.sample(range(-R, R + 1), 2)
                self.f = lambda x, a=self.a, r1=r1, r2=r2: a * (x - r1) * (x - r2)
            elif self.n_roots == 1:
                r = random.randint(-R, R)
                self.f = lambda x, a=self.a, r=r: a * (x - r) ** 2
            else:  # без вещественных корней: a·((x-h)^2 + c), знаки согласованы
                h = random.randint(-R, R)
                c = random.randint(1, R + 1)
                a = abs(self.a) * (1 if random.random() < 0.5 else -1)
                self.a = a
                self.f = lambda x, a=a, h=h, c=c: a * ((x - h) ** 2 + c)
        else:  # кубический
            self.n_roots = random.choice([1, 3])
            if self.n_roots == 3:
                r1, r2, r3 = random.sample(range(-R, R + 1), 3)
                self.f = lambda x, a=self.a, r=(r1, r2, r3): a * (x - r[0]) * (x - r[1]) * (x - r[2])
            else:  # один вещественный корень + неприводимый квадратичный множитель
                r = random.randint(-R, R)
                pp = random.randint(-2, 2)
                qq = (pp * pp) // 4 + random.randint(1, 3)  # дискриминант p²-4q < 0
                self.f = lambda x, a=self.a, r=r, pp=pp, qq=qq: a * (x - r) * (x * x + pp * x + qq)
        self.y0 = int(round(self.f(0)))

    def render_image(self):
        import matplotlib.pyplot as plt
        xmin, xmax = self.window
        xs = np.linspace(xmin, xmax, 400)
        ys = np.array([self.f(x) for x in xs], dtype=float)
        fig, ax = plt.subplots(figsize=(4.5, 4.0))
        ax.plot(xs, ys, color="#268bd2", linewidth=2)
        ax.axhline(0, color="black", linewidth=1)
        ax.axvline(0, color="black", linewidth=1)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_xticks(range(xmin, xmax + 1))
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("y = f(x)")
        pad = max(2.0, 0.1 * (ys.max() - ys.min() + 1))
        ax.set_ylim(ys.min() - pad, ys.max() + pad)
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "count_roots":
            return ((texts.t('s1', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        if self.task_type == "count_roots":
            self.solution_steps = [
                ((texts.t('s2', self.language))),
                ((texts.t('s3', self.language, n_roots=self.n_roots)))]
            self.final_answer = str(self.n_roots)
        else:
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((f"f(0) = {self.y0}."))]
            self.final_answer = str(self.y0)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        truth = self.n_roots if self.task_type == "count_roots" else self.y0
        return U.verify_int(prediction, int(truth))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
