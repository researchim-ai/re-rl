from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/graph_task.py

import random
import networkx as nx
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, ClassVar

from re_rl.tasks.math.logic.graph_algorithms_shared.base import _GraphBase
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import dijkstra_trace, kruskal_trace, traversal_trace, clustering_trace
from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace


class GraphTask(_GraphBase):
    """
    Генерирует и решает графовые задачи.
    
    Поддерживаемые типы: "shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient".
    
    Параметры сложности:
      - difficulty 1-2: 4-5 узлов, разреженный граф
      - difficulty 3-4: 6-8 узлов
      - difficulty 5-6: 8-12 узлов
      - difficulty 7-8: 12-16 узлов
      - difficulty 9-10: 16-25 узлов, плотный граф
      
    detail_level управляет количеством шагов решения.
    """
    
    TASK_TYPE = "graph"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_nodes": 4, "edge_prob": 0.4},
        2: {"num_nodes": 5, "edge_prob": 0.4},
        3: {"num_nodes": 6, "edge_prob": 0.45},
        4: {"num_nodes": 8, "edge_prob": 0.45},
        5: {"num_nodes": 10, "edge_prob": 0.5},
        6: {"num_nodes": 12, "edge_prob": 0.5},
        7: {"num_nodes": 14, "edge_prob": 0.55},
        8: {"num_nodes": 16, "edge_prob": 0.55},
        9: {"num_nodes": 20, "edge_prob": 0.6},
        10: {"num_nodes": 25, "edge_prob": 0.6},
    }
    
    def __init__(
        self, 
        task_type="shortest_path", 
        num_nodes=None, 
        edge_prob=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if num_nodes is None:
                num_nodes = preset.get("num_nodes", 10)
            if edge_prob is None:
                edge_prob = preset.get("edge_prob", 0.5)
        else:
            num_nodes = num_nodes or 10
            edge_prob = 0.5 if edge_prob is None else edge_prob
        self.task_type = task_type.lower()
        if num_nodes < 2 or not 0 <= edge_prob <= 1:
            raise ValueError((num_nodes, edge_prob))
        self.num_nodes = num_nodes
        self.edge_prob = edge_prob
        self.graph = None
        self.start = None
        self.end = None
        super().__init__("", language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def generate_graph(self):
        self.graph = nx.gnp_random_graph(self.num_nodes, self.edge_prob, seed=random.randint(1, 1000))
        components = sorted((sorted(c) for c in nx.connected_components(self.graph)), key=lambda c: c[0])
        for left, right in zip(components, components[1:]):
            self.graph.add_edge(left[0], right[0])
        self.n = self.num_nodes

    def _create_problem_description(self):
        if self.graph is None:
            self.generate_graph()
        if self.task_type == "shortest_path":
            nodes = list(self.graph.nodes())
            self.start = self.start if self.start is not None else random.choice(nodes)
            self.end = self.end if self.end is not None else random.choice(nodes)
            while self.end == self.start:
                self.end = random.choice(nodes)
            task_description = texts.t('s0', self.language, start=self.start, end=self.end)
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        # Остальные типы остаются без изменений
        elif self.task_type == texts.t('s2', self.language):
            for (u, v) in self.graph.edges():
                if 'weight' not in self.graph[u][v]:
                    self.graph[u][v]['weight'] = random.randint(1, 10)
            task_description = texts.t('s3', self.language)
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        elif self.task_type == "diameter":
            task_description = texts.t('s5', self.language)
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        elif self.task_type == "clustering_coefficient":
            task_description = texts.t('s7', self.language)
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        else:
            return PROMPT_TEMPLATES["default"]["no_solution"].get(self.language, PROMPT_TEMPLATES["default"]["no_solution"]["en"])

    def solve(self):
        self.description = self._create_problem_description()
        self.edges = [(a, b, data.get('weight', 1)) for a, b, data in sorted(self.graph.edges(data=True))]
        self.description += texts.t('graph_data', self.language, n=self.n, edges=self.edges)
        if self.task_type == 'shortest_path':
            _, self.algorithm_trace = dijkstra_trace(self.n, self.edges, self.start, self.end)
            self.solution_steps = render_trace(self.algorithm_trace, 'dijkstra', self.language)
            self.final_answer = str(self.algorithm_trace[-1]['path'])
        elif self.task_type == 'minimum_spanning_tree':
            _, self.algorithm_trace = kruskal_trace(self.n, self.edges)
            self.solution_steps = render_trace(self.algorithm_trace, 'kruskal', self.language)
            self.final_answer = str([(a, b, {'weight': weight}) for a, b, weight in self.algorithm_trace[-1]['edges']])
        elif self.task_type == 'diameter':
            self.algorithm_trace, eccentricities = [], []
            for source in range(self.n):
                eccentricity, events = traversal_trace(self.n, [(a, b) for a, b, _ in self.edges], 'all_distances', source)
                eccentricities.append(eccentricity)
                self.algorithm_trace.extend(events)
            answer = max(eccentricities)
            self.algorithm_trace.append(dict(event='diameter', values=eccentricities, answer=answer))
            self.solution_steps = render_trace(self.algorithm_trace, 'walk', self.language)
            self.final_answer = str(answer)
        elif self.task_type == 'clustering_coefficient':
            answer, self.algorithm_trace = clustering_trace(self.n, [(a, b) for a, b, _ in self.edges])
            self.solution_steps = render_trace(self.algorithm_trace, 'cluster', self.language)
            self.final_answer = str(answer)
        else:
            raise ValueError(self.task_type)

    def get_task_type(self):
        return "graph"

    @classmethod
    def generate_random_task(cls, only_valid=False, num_nodes=None, edge_prob=None, language='ru',
                             detail_level=3, reasoning_mode=False, difficulty=5, task_type=None, **kwargs):
        task_type = task_type or random.choice(['shortest_path', 'minimum_spanning_tree', 'diameter', 'clustering_coefficient'])
        task = cls(task_type=task_type, num_nodes=num_nodes, edge_prob=edge_prob, language=language,
                   detail_level=detail_level, reasoning_mode=reasoning_mode, difficulty=difficulty)
        task.solve()
        return task
