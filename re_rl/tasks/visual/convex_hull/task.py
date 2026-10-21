"""ConvexHullVisualTask — визуальный вариант: точки на плоскости → число вершин
выпуклой оболочки. Координаты считываются с рисунка (в тексте их нет)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.geometry.computational_geometry_task import ComputationalGeometryTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class ConvexHullVisualTask(VisualTaskMixin, ComputationalGeometryTask):
    TASK_TYPE = texts.literal('literals.s1')
    TASK_TYPES = ["convex_hull"]

    def __init__(self, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        super().__init__(task_type="convex_hull", language=language, detail_level=detail_level,
                         difficulty=difficulty, output_format=output_format,
                         reasoning_mode=reasoning_mode, augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        import matplotlib.pyplot as plt
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        fig, ax = plt.subplots(figsize=(4.8, 4.6))
        ax.scatter(xs, ys, s=70, color="#268bd2", edgecolors="#0b3d5c", zorder=3)
        c = self.coord
        ax.set_xlim(-c - 1, c + 1)
        ax.set_ylim(-c - 1, c + 1)
        ax.set_xticks(range(-c, c + 1, max(1, c // 6)))
        ax.set_yticks(range(-c, c + 1, max(1, c // 6)))
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_aspect("equal")
        ax.set_title(texts.t('s2', self.language))
        return fig_to_image(fig)

    def _descr_visual(self, language):
        return ((texts.t('s0', language)))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
