"""CircuitResistanceVisualTask — визуальный вариант последовательно-параллельной
сети резисторов: по схеме найти эквивалентное сопротивление. Номиналы и
топология считываются со схемы (в тексте их нет)."""

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.physics.networks.series_parallel_task import SeriesParallelNetworkTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class CircuitResistanceVisualTask(VisualTaskMixin, SeriesParallelNetworkTask):
    TASK_TYPE = "circuit_resistance_image"
    TASK_TYPES = ["resistor"]

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False, **kwargs):
        super().__init__(task_type="resistor", language=language, detail_level=detail_level,
                         difficulty=difficulty, output_format=output_format,
                         reasoning_mode=reasoning_mode)
        self.description = self._descr_visual(language)

    # --- размеры поддерева в условных единицах ---
    def _size(self, node):
        if node[0] == "leaf":
            return (1, 1)
        wa, ha = self._size(node[1])
        wb, hb = self._size(node[2])
        if node[0] == "series":
            return (wa + wb, max(ha, hb))
        return (max(wa, wb), ha + hb)

    def _draw(self, ax, node, x, y, w, h):
        ymid = y + h / 2
        if node[0] == "leaf":
            bw = min(0.6, w * 0.6)
            bx = x + (w - bw) / 2
            ax.plot([x, bx], [ymid, ymid], color="#333", lw=1.4)
            ax.plot([bx + bw, x + w], [ymid, ymid], color="#333", lw=1.4)
            from matplotlib.patches import Rectangle
            ax.add_patch(Rectangle((bx, ymid - 0.16), bw, 0.32, fill=True,
                                   facecolor="#fdf6e3", edgecolor="#333", lw=1.4, zorder=3))
            ax.text(bx + bw / 2, ymid, f"{node[1]}Ω", ha="center", va="center",
                    fontsize=9, zorder=4)
            return
        if node[0] == "series":
            sa = self._size(node[1]); sb = self._size(node[2])
            wa = w * sa[0] / (sa[0] + sb[0])
            self._draw(ax, node[1], x, y, wa, h)
            self._draw(ax, node[2], x + wa, y, w - wa, h)
            return
        # parallel
        sa = self._size(node[1]); sb = self._size(node[2])
        ha = h * sa[1] / (sa[1] + sb[1])
        hb = h - ha
        self._draw(ax, node[1], x, y + hb, w, ha)   # верхняя ветвь
        self._draw(ax, node[2], x, y, w, hb)        # нижняя ветвь
        ya = y + hb + ha / 2
        yb = y + hb / 2
        ax.plot([x, x], [ya, yb], color="#333", lw=1.4)          # левая шина
        ax.plot([x + w, x + w], [ya, yb], color="#333", lw=1.4)  # правая шина

    def render_image(self):
        import matplotlib.pyplot as plt
        W, H = self._size(self.tree)
        fig, ax = plt.subplots(figsize=(min(9, 1.3 * W + 1.5), min(7, 1.0 * H + 1.2)))
        self._draw(ax, self.tree, 0.6, 0.3, W, max(1, H))
        ymid = 0.3 + max(1, H) / 2
        ax.plot([0, 0.6], [ymid, ymid], color="#333", lw=1.4)
        ax.plot([0.6 + W, 1.2 + W], [ymid, ymid], color="#333", lw=1.4)
        ax.text(0.05, ymid + 0.2, "A", fontsize=12, fontweight="bold")
        ax.text(1.1 + W, ymid + 0.2, "B", fontsize=12, fontweight="bold")
        ax.set_xlim(-0.2, 1.4 + W)
        ax.set_ylim(0, max(1, H) + 0.6)
        ax.axis("off")
        ax.set_aspect("equal")
        ax.set_title("Схема резисторов")
        return fig_to_image(fig)

    def _descr_visual(self, language):
        ru = language == "ru"
        return (("На схеме — сеть резисторов (номиналы указаны на элементах, в омах). Найдите "
                 "эквивалентное сопротивление между точками A и B.") if ru else
                ("The schematic shows a resistor network (values are labeled on the elements, in "
                 "ohms). Find the equivalent resistance between points A and B."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task
