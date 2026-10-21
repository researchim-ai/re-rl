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















