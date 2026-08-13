"""Визуальный вариант площади многоугольника (matplotlib).

Наследует логику от :class:`ShoelaceAreaTask`: многоугольник рисуется на
координатной сетке, вершины подписаны координатами. Нужно найти площадь.
Проверка числовая (наследуется).
"""

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.geometry.shoelace_area_task import ShoelaceAreaTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class ShoelaceAreaVisualTask(VisualTaskMixin, ShoelaceAreaTask):
    TASK_TYPE = "shoelace_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        import matplotlib.pyplot as plt
        pts = self._points + [self._points[0]]
        xs = [x for x, _ in pts]
        ys = [y for _, y in pts]
        fig, ax = plt.subplots(figsize=(4.8, 4.8))
        ax.plot(xs, ys, "-o", color="#2aa198", linewidth=2, markersize=6)
        ax.fill(xs, ys, color="#2aa198", alpha=0.15)
        for x, y in self._points:
            ax.annotate(f"({x}, {y})", (x, y), textcoords="offset points", xytext=(5, 5),
                        fontsize=9)
        lim = self.coord + 2
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.axhline(0, color="#999999", linewidth=0.8)
        ax.axvline(0, color="#999999", linewidth=0.8)
        ax.set_aspect("equal")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title("Многоугольник по вершинам")
        return fig_to_image(fig)

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На координатной плоскости изображён многоугольник с {self.n} вершинами (их "
                 f"координаты подписаны). Найдите его площадь.") if ru else
                (f"The coordinate plane shows a polygon with {self.n} vertices (their coordinates "
                 f"are labeled). Find its area."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
