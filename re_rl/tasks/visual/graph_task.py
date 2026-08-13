"""Визуальные варианты графовых задач: граф рисуется через networkx, а логика и
`verify` наследуются от текстовых задач.

- ``shortest_path_image`` — вес кратчайшего пути (исток/сток выделены цветом);
- ``mst_image``           — суммарный вес минимального остовного дерева;
- ``graph_coloring_image``— хроматическое число / k-раскрашиваемость;
- ``topological_sort_image`` — топологический порядок / наличие цикла (орграф);
- ``max_flow_image``      — величина максимального потока (сеть с пропускными).
"""

import networkx as nx

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_task import (
    WeightedShortestPathTask, MSTWeightTask, GraphColoringTask,
    TopologicalSortTask, MaxFlowTask,
)
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


def _draw_graph(n, edges, directed=False, weighted=False, highlight=None, seed=7, title=""):
    """edges: (a,b) либо (a,b,w). highlight: dict{node: color}. Возвращает PIL.Image."""
    import matplotlib.pyplot as plt
    G = (nx.DiGraph if directed else nx.Graph)()
    G.add_nodes_from(range(n))
    labels = {}
    for e in edges:
        if weighted:
            a, b, w = e
            G.add_edge(a, b, weight=w)
            labels[(a, b)] = w
        else:
            a, b = e[0], e[1]
            G.add_edge(a, b)
    pos = nx.spring_layout(G, seed=seed)
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    colors = [(highlight or {}).get(v, "#cfe8ff") for v in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=colors, edgecolors="#333333",
                           node_size=650, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, ax=ax)
    edge_kw = dict(width=1.6, edge_color="#555555", ax=ax)
    if directed:
        edge_kw.update(arrows=True, arrowsize=18, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_edges(G, pos, **edge_kw)
    if weighted:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10, ax=ax)
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
        return _draw_graph(self.n, self.edges, weighted=True, highlight=hl,
                           seed=self.n + self.src, title="Взвешенный граф")

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
        return _draw_graph(self.n, self.edges, weighted=True, seed=self.n * 3,
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


class GraphColoringVisualTask(VisualTaskMixin, GraphColoringTask):
    TASK_TYPE = "graph_coloring_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype=None, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment, subtype=subtype)
        self.description = self._descr_visual(language)

    def render_image(self):
        return _draw_graph(self.n, self.edges, seed=self.n * 5 + len(self.edges),
                           title="Неориентированный граф")

    def _descr_visual(self, language):
        ru = language == "ru"
        if self.subtype == "chromatic":
            return (("На рисунке — неориентированный граф. Найдите его хроматическое число "
                     "(минимальное число цветов для правильной раскраски вершин).") if ru else
                    ("The figure shows an undirected graph. Find its chromatic number (minimum "
                     "number of colors for a proper vertex coloring)."))
        return ((f"На рисунке — неориентированный граф. Можно ли правильно раскрасить его вершины "
                 f"в {self.k} цвета? Ответьте да/нет.") if ru else
                (f"The figure shows an undirected graph. Can its vertices be properly colored with "
                 f"{self.k} colors? Answer yes/no."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True,
                             subtype=None, task_type=None, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, subtype=subtype or task_type)
        task.solve()
        return task


class TopoSortVisualTask(VisualTaskMixin, TopologicalSortTask):
    TASK_TYPE = "topological_sort_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype=None, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment, subtype=subtype)
        self.description = self._descr_visual(language)

    def render_image(self):
        return _draw_graph(self.n, self.edges, directed=True, seed=self.n * 7,
                           title="Ориентированный граф")

    def _descr_visual(self, language):
        ru = language == "ru"
        if self.subtype == "has_cycle":
            return (("На рисунке — ориентированный граф (стрелки — дуги). Есть ли в нём "
                     "ориентированный цикл? Ответьте да/нет.") if ru else
                    ("The figure shows a directed graph (arrows are arcs). Does it contain a "
                     "directed cycle? Answer yes/no."))
        return (("На рисунке — ориентированный ациклический граф (стрелки — дуги). Выпишите "
                 "топологический порядок вершин (слева направо).") if ru else
                ("The figure shows a directed acyclic graph (arrows are arcs). Output a "
                 "topological ordering of the vertices (left to right)."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True,
                             subtype=None, task_type=None, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, subtype=subtype or task_type)
        task.solve()
        return task


class MaxFlowVisualTask(VisualTaskMixin, MaxFlowTask):
    TASK_TYPE = "max_flow_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        hl = {self.s: "#8ce68c", self.t: "#ff8c8c"}
        return _draw_graph(self.n, self.cap_edges, directed=True, weighted=True,
                           highlight=hl, seed=self.n * 11, title="Транспортная сеть")

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На рисунке — транспортная сеть (стрелки — дуги, числа — пропускные "
                 f"способности). Исток {self.s} (зелёный), сток {self.t} (красный). Найдите "
                 f"величину максимального потока из истока в сток.") if ru else
                (f"The figure shows a flow network (arrows are arcs, numbers are capacities). "
                 f"Source {self.s} (green), sink {self.t} (red). Find the maximum flow value from "
                 f"source to sink."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
