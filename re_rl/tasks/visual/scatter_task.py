"""ScatterPlotTask — чтение диаграммы рассеяния: определить характер связи между
переменными (положительная / отрицательная / отсутствует)."""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


def _pearson(xs, ys) -> float:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    return sxy / (sxx * syy) ** 0.5


class ScatterPlotTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "scatter_plot"
    TASK_TYPES = ["trend"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 10}, 2: {"n": 12}, 3: {"n": 14}, 4: {"n": 16}, 5: {"n": 18},
        6: {"n": 20}, 7: {"n": 24}, 8: {"n": 28}, 9: {"n": 32}, 10: {"n": 40},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = "trend"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.kind = random.choice(["positive", "negative", "none"])
        for _ in range(200):
            xs = [random.uniform(0, 10) for _ in range(self.n)]
            if self.kind == "none":
                ys = [random.uniform(0, 10) for _ in range(self.n)]
            else:
                slope = random.uniform(0.7, 1.6) * (1 if self.kind == "positive" else -1)
                noise = random.uniform(0.6, 1.4)
                ys = [slope * x + random.gauss(0, noise) + 5 for x in xs]
            r = _pearson(xs, ys)
            ok = ((self.kind == "positive" and r > 0.55) or
                  (self.kind == "negative" and r < -0.55) or
                  (self.kind == "none" and abs(r) < 0.2))
            if ok:
                self.xs, self.ys, self.r = xs, ys, r
                return
        # запасной вариант — гарантированно корректный
        self.xs = list(range(self.n))
        self.ys = list(range(self.n)) if self.kind != "negative" else list(range(self.n, 0, -1))
        if self.kind == "none":
            self.ys = [random.uniform(0, 10) for _ in range(self.n)]
        self.r = _pearson(self.xs, self.ys)

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.0, 4.2))
        ax.scatter(self.xs, self.ys, s=45, color="#268bd2", edgecolors="#0b3d5c")
        ax.set_xlabel("X"); ax.set_ylabel("Y")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title("Диаграмма рассеяния")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        return (("На диаграмме рассеяния показаны пары (X, Y). Какова связь между X и Y? Ответьте "
                 "одним словом: «положительная», «отрицательная» или «отсутствует».") if ru else
                ("The scatter plot shows pairs (X, Y). What is the relationship between X and Y? "
                 "Answer with one word: 'positive', 'negative', or 'none'."))

    def solve(self):
        ru = self.language == "ru"
        label = {"positive": ("положительная" if ru else "positive"),
                 "negative": ("отрицательная" if ru else "negative"),
                 "none": ("отсутствует" if ru else "none")}[self.kind]
        self.solution_steps = [
            ("Оцениваем направление облака точек (растёт/убывает/без закономерности)." if ru else
             "Assess the direction of the point cloud (rising/falling/no pattern)."),
            (f"Связь: {label} (r≈{self.r:.2f})." if ru else f"Relationship: {label} (r≈{self.r:.2f}).")]
        self.final_answer = label

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        roots = {
            "positive": ["положительн", "прям", "posit", "растет", "возраст"],
            "negative": ["отрицательн", "обратн", "negativ", "убыва"],
            "none": ["отсутств", "нет свя", "нет зав", "none", "no correl", "без свя"],
        }[self.kind]
        norm = U.normalize(prediction)
        return 1.0 if any(r in norm for r in roots) else 0.0

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3,
                             difficulty=5, reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
