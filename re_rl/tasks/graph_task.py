# re_rl/tasks/graph_task.py

import random
import networkx as nx
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class GraphTask(BaseMathTask):
    """
    Класс для генерации и решения графовых задач.
    Поддерживаемые типы: "shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient".
    """
    def __init__(self, task_type="shortest_path", num_nodes=10, edge_prob=0.3, language: str = "ru"):
        self.task_type = task_type.lower()
        self.num_nodes = num_nodes
        self.edge_prob = edge_prob
        self.graph = None
        self.start = None
        self.end = None
        super().__init__("", language)

    def generate_graph(self):
        self.graph = nx.gnp_random_graph(self.num_nodes, self.edge_prob, seed=random.randint(1,1000), directed=False)
        if not nx.is_connected(self.graph):
            largest_cc = max(nx.connected_components(self.graph), key=len)
            self.graph = self.graph.subgraph(largest_cc).copy()

    def _create_problem_description(self):
        self.generate_graph()
        if self.task_type=="shortest_path":
            nodes = list(self.graph.nodes())
            self.start = random.choice(nodes)
            self.end = random.choice(nodes)
            while self.end == self.start:
                self.end = random.choice(nodes)
            task_description = f"кратчайший путь между узлами {self.start} и {self.end}"
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        elif self.task_type=="minimum_spanning_tree":
            for (u,v) in self.graph.edges():
                self.graph[u][v]['weight'] = random.randint(1,10)
            task_description = "минимальное остовное дерево данного графа"
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        elif self.task_type=="diameter":
            task_description = "диаметр данного графа"
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        elif self.task_type=="clustering_coefficient":
            task_description = "средний коэффициент кластеризации данного графа"
            return PROMPT_TEMPLATES["graph"]["problem"][self.language].format(task_description=task_description)
        else:
            return "Неизвестный тип задачи."

    def solve(self):
        self.description = self._create_problem_description()
        if self.task_type=="shortest_path":
            try:
                path = nx.shortest_path(self.graph, source=self.start, target=self.end)
                step = f"Используем алгоритм Дейкстры для поиска кратчайшего пути: {path}."
                self.solution_steps.append(PROMPT_TEMPLATES["graph"]["step2"][self.language].format(solution_step=step))
                self.final_answer = str(path)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type=="minimum_spanning_tree":
            try:
                mst = nx.minimum_spanning_tree(self.graph)
                edges = list(mst.edges(data=True))
                step = f"Найденное минимальное остовное дерево: {edges}."
                self.solution_steps.append(PROMPT_TEMPLATES["graph"]["step2"][self.language].format(solution_step=step))
                self.final_answer = str(edges)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type=="diameter":
            try:
                diam = nx.diameter(self.graph)
                step = f"Диаметр графа: {diam}."
                self.solution_steps.append(PROMPT_TEMPLATES["graph"]["step2"][self.language].format(solution_step=step))
                self.final_answer = str(diam)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type=="clustering_coefficient":
            try:
                avg_coeff = nx.average_clustering(self.graph)
                step = f"Средний коэффициент кластеризации: {avg_coeff}."
                self.solution_steps.append(PROMPT_TEMPLATES["graph"]["step2"][self.language].format(solution_step=step))
                self.final_answer = str(avg_coeff)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        else:
            self.solution_steps.append("Неизвестный тип задачи.")
            self.final_answer = "Нет решения"

    def get_task_type(self):
        return "graph"

    @classmethod
    def generate_random_task(cls, only_valid=False, num_nodes=10, edge_prob=0.3, language: str = "ru"):
        task_types = ["shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient"]
        task_type = random.choice(task_types)
        task = cls(task_type=task_type, num_nodes=num_nodes, edge_prob=edge_prob, language=language)
        task.solve()
        return task
