from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import networkx as nx

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import dijkstra_trace, kruskal_trace, flow_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace


class GraphJustificationTask(_GraphBase):
    """Graph algorithms with explicit method justification."""

    TASK_TYPE = "graph_justification"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_nodes": 5, "edge_prob": 0.35, "task_type": "shortest_path"},
        2: {"num_nodes": 6, "edge_prob": 0.35, "task_type": "shortest_path"},
        3: {"num_nodes": 7, "edge_prob": 0.4, "task_type": "shortest_path"},
        4: {"num_nodes": 7, "edge_prob": 0.45, "task_type": "mst"},
        5: {"num_nodes": 8, "edge_prob": 0.45, "task_type": "mst"},
        6: {"num_nodes": 9, "edge_prob": 0.5, "task_type": "mst"},
        7: {"num_nodes": 7, "edge_prob": 0.35, "task_type": "max_flow"},
        8: {"num_nodes": 8, "edge_prob": 0.35, "task_type": "max_flow"},
        9: {"num_nodes": 9, "edge_prob": 0.4, "task_type": "mixed"},
        10: {"num_nodes": 10, "edge_prob": 0.4, "task_type": "mixed"},
    }

    def __init__(
        self,
        task_type: Optional[str] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_nodes: Optional[int] = None,
        edge_prob: Optional[float] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or str(preset.get("task_type", "mixed"))
        if self.task_type == "mixed":
            self.task_type = random.choice(["shortest_path", "mst", "max_flow"])
        self.num_nodes = num_nodes if num_nodes is not None else int(preset.get("num_nodes", 8))
        self.edge_prob = edge_prob if edge_prob is not None else float(preset.get("edge_prob", 0.4))
        self.augment = augment
        self._instance_graph = None
        super().__init__("", language=language, detail_level=detail_level, output_format=output_format, reasoning_mode=reasoning_mode)

    def _build_weighted_graph(self) -> nx.Graph:
        g = nx.gnp_random_graph(self.num_nodes, self.edge_prob, seed=random.randint(1, 10_000))
        if not nx.is_connected(g):
            nodes = list(g.nodes())
            for i in range(len(nodes) - 1):
                g.add_edge(nodes[i], nodes[i + 1])
        for u, v in g.edges():
            g[u][v]["weight"] = random.randint(1, 12)
            g[u][v]["capacity"] = random.randint(3, 20)
        return g

    def solve(self):
        section = PROMPT_TEMPLATES["graph_justification"]
        if self._instance_graph is None:
            self._instance_graph = self._build_weighted_graph()
        g = self._instance_graph
        self.n = self.num_nodes
        edges = [(u, v, g[u][v]["weight"]) for u, v in g.edges()]
        self.edges = edges

        if self.task_type == "shortest_path":
            source = 0
            target = self.num_nodes - 1
            self.description = get_template(
                section, "problem_shortest", self.language, augment=self.augment, source=source, target=target, edges=edges
            )
            self.src, self.dst = source, target
            dist, self.algorithm_trace = dijkstra_trace(self.n, edges, source, target)
            path = self.algorithm_trace[-1]["path"]
            self.solution_steps = render_trace(self.algorithm_trace, "dijkstra", self.language)
            self.final_answer = f"distance={dist};path={'-'.join(str(x) for x in path)}"
            return

        if self.task_type == "mst":
            self.description = get_template(section, "problem_mst", self.language, augment=self.augment, edges=edges)
            total_w, self.algorithm_trace = kruskal_trace(self.n, edges)
            tree_edges = sorted((min(u, v), max(u, v)) for u, v, _ in self.algorithm_trace[-1]['edges'])
            self.solution_steps = render_trace(self.algorithm_trace, 'kruskal', self.language)
            self.final_answer = f"weight={total_w};edges={tree_edges}"
            return

        dg = nx.DiGraph()
        for u, v in g.edges():
            cap = g[u][v]["capacity"]
            dg.add_edge(u, v, capacity=cap)
            dg.add_edge(v, u, capacity=max(1, cap // 2))
        source = 0
        sink = self.num_nodes - 1
        self.description = get_template(
            section, texts.t('s0', self.language), self.language, augment=self.augment, source=source, sink=sink, edges=list(dg.edges(data=True))
        )
        self.s, self.t = source, sink
        self.cap_edges = [(a, b, d["capacity"]) for a, b, d in dg.edges(data=True)]
        value, self.algorithm_trace = flow_trace(self.n, self.cap_edges, source, sink)
        self.solution_steps = render_trace(self.algorithm_trace, "flow", self.language)
        self.final_answer = f"max_flow={value}"

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "GraphJustificationTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
