"""SlopeReadTask — наклон прямой и пересечение с осью Oy по сетке.

Прямая проходит через целые точки (0, b) и (1, b + m), m — целое.
В тексте координат нет.

Подтипы: ``slope`` (изменение y при x + 1), ``intercept`` (y при x = 0).
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class SlopeReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "slope_read"
    TASK_TYPES = ["slope", "intercept"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mmax": 2}, 2: {"mmax": 2}, 3: {"mmax": 2}, 4: {"mmax": 3}, 5: {"mmax": 3},
        6: {"mmax": 3}, 7: {"mmax": 4}, 8: {"mmax": 4}, 9: {"mmax": 4}, 10: {"mmax": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.mmax = int(p["mmax"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.m = random.randint(-self.mmax, self.mmax)
        self.b = random.randint(0, 5)
        self.x1 = 4
        self.answer = self.m if self.task_type == "slope" else self.b

    def render_image(self):
        import matplotlib.pyplot as plt

        xs = [0, 1, self.x1]
        ys = [self.b + self.m * x for x in xs]
        pad = 1
        ymin = min(ys + [0]) - pad
        ymax = max(ys + [0]) + pad
        fig, ax = plt.subplots(figsize=(5.0, 4.6))
        ax.set_xlim(-0.6, self.x1 + 0.6)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks(range(0, self.x1 + 1))
        ax.set_yticks(range(int(ymin) + 1, int(ymax)))
        ax.grid(True, linestyle="-", alpha=0.45)
        ax.axhline(0, color="#333", lw=1.1)
        ax.axvline(0, color="#333", lw=1.1)
        ax.plot([0, self.x1], [self.b, self.b + self.m * self.x1], color="#268bd2", lw=2.2, zorder=2)
        ax.scatter(xs, ys, s=36, color="#cb4b16", zorder=3)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "slope":
            return (("На координатной сетке проведена прямая. Чему равен её наклон — "
                     "на сколько меняется y, когда x увеличивается на 1?") if ru else
                    ("A straight line is drawn on the grid. What is its slope — "
                     "how much does y change when x increases by 1?"))
        return (("Чему равен y в точке, где прямая пересекает ось Oy?") if ru else
                ("What is y where the line crosses the Oy axis?"))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "slope":
            step = ((f"От x = 0 до x = 1 величина y меняется на {self.m}.") if ru else
                    (f"From x = 0 to x = 1, y changes by {self.m}."))
        else:
            step = ((f"Прямая пересекает ось Oy в точке (0, {self.b}).") if ru else
                    (f"The line crosses the Oy axis at (0, {self.b})."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3,
                             difficulty=5, reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
