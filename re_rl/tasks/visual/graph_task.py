"""Визуальные варианты графовых задач: граф рисуется через networkx, а логика и
`verify` наследуются от текстовых задач.

- ``shortest_path_image`` — вес кратчайшего пути (исток/сток выделены цветом);
- ``mst_image``           — суммарный вес минимального остовного дерева.
"""

from typing import Optional

import networkx as nx

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_task import (
    WeightedShortestPathTask, MSTWeightTask,
)
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


def _draw_weighted_graph(n, edges, highlight=None, seed=7, title=""):
    """edges: список (a, b, w). highlight: dict{node: color}. Возвращает PIL.Image."""
    import matplotlib.pyplot as plt
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for a, b, w in edges:
        G.add_edge(a, b, weight=w)
    pos = nx.spring_layout(G, seed=seed)
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    colors = [(highlight or {}).get(v, "#cfe8ff") for v in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=colors, edgecolors="#333333",
                           node_size=650, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, ax=ax)
    nx.draw_networkx_edges(G, pos, width=1.6, edge_color="#555555", ax=ax)
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels={(a, b): w for a, b, w in edges}, font_size=10, ax=ax)
    ax.set_title(title)
    ax.axis("off")
    return fig_to_image(fig)


class ShortestPathVisualTask(VisualTaskMixin, WeightedShortestPathTask):
    TASK_TYPE = "shortest_path_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        hl = {self.src: "#8ce68c", self.dst: "#ff8c8c"}
        return _draw_weighted_graph(self.n, self.edges, highlight=hl, seed=self.n + self.src,
                                    title="Взвешенный граф")

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На рисунке — взвешенный неориентированный граф (числа на рёбрах — веса). "
                 f"Найдите вес кратчайшего пути между вершиной {self.src} (зелёная) и вершиной "
                 f"{self.dst} (красная).") if ru else
                (f"The figure shows a weighted undirected graph (numbers on edges are weights). "
                 f"Find the weight of the shortest path between vertex {self.src} (green) and "
                 f"vertex {self.dst} (red)."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task


class MSTVisualTask(VisualTaskMixin, MSTWeightTask):
    TASK_TYPE = "mst_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        return _draw_weighted_graph(self.n, self.edges, seed=self.n * 3,
                                    title="Взвешенный связный граф")

    def _descr_visual(self, language):
        ru = language == "ru"
        return (("На рисунке — взвешенный связный граф (числа на рёбрах — веса). Найдите "
                 "суммарный вес минимального остовного дерева.") if ru else
                ("The figure shows a weighted connected graph (numbers on edges are weights). "
                 "Find the total weight of the minimum spanning tree."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
