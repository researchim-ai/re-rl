"""Визуальный вариант логической схемы: DAG из вентилей (matplotlib).

Наследует логику от :class:`BooleanCircuitTask` (подтипы evaluate/count).
Схема рисуется послойно: входы слева, выход справа.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


from collections import defaultdict

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.boolean_circuit_task import BooleanCircuitTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image

_GATE_COLOR = {"AND": "#8ce68c", "OR": "#9ec7ff", "XOR": "#ffd27f", "NOT": "#ff9e9e"}


class BooleanCircuitVisualTask(VisualTaskMixin, BooleanCircuitTask):
    TASK_TYPE = texts.literal('literals.s2')

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype=None, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment, subtype=subtype or kwargs.get("task_type"))
        self.description = self._descr_visual(language)

    def _layers(self):
        layer = {i: 0 for i in range(self.k)}
        for gi, (op, a, b) in enumerate(self.gates):
            node = self.k + gi
            refs = [a] if op == "NOT" else [a, b]
            layer[node] = 1 + max(layer[r] for r in refs)
        return layer

    def render_image(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
        layer = self._layers()
        by_layer = defaultdict(list)
        for node, l in layer.items():
            by_layer[l].append(node)
        pos = {}
        for l, nodes in by_layer.items():
            nodes.sort()
            for j, node in enumerate(nodes):
                y = (j - (len(nodes) - 1) / 2) * 1.4
                pos[node] = (l * 2.2, y)
        fig, ax = plt.subplots(figsize=(1.6 + max(layer.values()) * 1.5, 4.8))
        ax.axis("off")
        out_node = self.total - 1

        def label(node):
            if node < self.k:
                s = f"x{node + 1}"
                if self.subtype == "evaluate":
                    s += f"={self.inputs[node]}"
                return s
            op, a, b = self.gates[node - self.k]
            return f"{op}\ng{node - self.k + 1}"

        # рёбра
        for gi, (op, a, b) in enumerate(self.gates):
            node = self.k + gi
            for r in ([a] if op == "NOT" else [a, b]):
                x1, y1 = pos[r]; x2, y2 = pos[node]
                ax.add_patch(FancyArrowPatch((x1 + 0.55, y1), (x2 - 0.55, y2),
                                             arrowstyle="-|>", mutation_scale=12,
                                             color="#666666", lw=1.3))
        # узлы
        for node, (x, y) in pos.items():
            if node < self.k:
                color = "#eeeeee"
            else:
                op = self.gates[node - self.k][0]
                color = _GATE_COLOR.get(op, "#dddddd")
            edge = "#d33682" if node == out_node else "#333333"
            lw = 2.6 if node == out_node else 1.4
            ax.add_patch(FancyBboxPatch((x - 0.55, y - 0.42), 1.1, 0.84,
                                        boxstyle="round,pad=0.02", facecolor=color,
                                        edgecolor=edge, lw=lw))
            ax.text(x, y, label(node), ha="center", va="center", fontsize=10)
        xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
        ax.set_xlim(min(xs) - 1, max(xs) + 1)
        ax.set_ylim(min(ys) - 1, max(ys) + 1)
        ax.set_title(texts.t('s3', self.language))
        return fig_to_image(fig)

    def _descr_visual(self, language):
        out = f"g{self.g}"
        if self.subtype == "evaluate":
            return ((texts.t('s1', language, k=self.k, out=out)))
        return ((texts.t('s0', language, k=self.k, out=out, v2=2 ** self.k)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True,
                             subtype=None, task_type=None, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, subtype=subtype or task_type)
        task.solve()
        return task
