import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import networkx as nx

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class GraphJustificationTask(BaseMathTask):
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
        g = self._build_weighted_graph()
        edges = [(u, v, g[u][v]["weight"]) for u, v in g.edges()]

        if self.task_type == "shortest_path":
            source = 0
            target = self.num_nodes - 1
            self.description = get_template(
                section, "problem_shortest", self.language, augment=self.augment, source=source, target=target, edges=edges
            )
            path = nx.shortest_path(g, source=source, target=target, weight="weight")
            dist = nx.shortest_path_length(g, source=source, target=target, weight="weight")
            self.solution_steps.append(get_template(section, "justify_dijkstra", self.language, augment=False))
            self.final_answer = f"distance={dist};path={'-'.join(str(x) for x in path)}"
            return

        if self.task_type == "mst":
            self.description = get_template(section, "problem_mst", self.language, augment=self.augment, edges=edges)
            mst = nx.minimum_spanning_tree(g, weight="weight")
            total_w = sum(d["weight"] for _, _, d in mst.edges(data=True))
            tree_edges = sorted((min(u, v), max(u, v)) for u, v in mst.edges())
            self.solution_steps.append(get_template(section, "justify_mst", self.language, augment=False))
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
            section, "problem_max_flow", self.language, augment=self.augment, source=source, sink=sink, edges=list(dg.edges(data=True))
        )
        value, _ = nx.maximum_flow(dg, source, sink, capacity="capacity")
        self.solution_steps.append(get_template(section, "justify_maxflow", self.language, augment=False))
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
