import random
import networkx as nx

class GraphTask:
    """
    Класс для генерации и решения графовых задач.
    
    Поддерживаемые типы задач:
      - "shortest_path": найти кратчайший путь между двумя узлами.
      - "minimum_spanning_tree": найти минимальное остовное дерево графа.
      - "diameter": найти диаметр графа (максимальное расстояние между любыми двумя узлами).
      - "clustering_coefficient": вычислить средний коэффициент кластеризации графа.
    """
    def __init__(self, task_type="shortest_path", num_nodes=10, edge_prob=0.3):
        self.task_type = task_type
        self.num_nodes = num_nodes
        self.edge_prob = edge_prob
        self.graph = None
        self.problem = ""
        self.solution_steps = []
        self.final_answer = None
        # Для задачи кратчайшего пути:
        self.start = None
        self.end = None

    def generate_graph(self):
        # Генерируем случайный неориентированный граф
        self.graph = nx.gnp_random_graph(self.num_nodes, self.edge_prob, seed=random.randint(1, 1000), directed=False)
        # Если граф не связный, выбираем крупнейшую связную компоненту
        if not nx.is_connected(self.graph):
            largest_cc = max(nx.connected_components(self.graph), key=len)
            self.graph = self.graph.subgraph(largest_cc).copy()

    def create_problem_description(self):
        self.generate_graph()
        if self.task_type == "shortest_path":
            nodes = list(self.graph.nodes())
            self.start = random.choice(nodes)
            self.end = random.choice(nodes)
            while self.end == self.start:
                self.end = random.choice(nodes)
            self.problem = (
                f"Найди кратчайший путь между узлами {self.start} и {self.end}.\n"
                f"Граф задан ребрами: {list(self.graph.edges())}"
            )
        elif self.task_type == "minimum_spanning_tree":
            # Присваиваем случайные веса ребрам
            for (u, v) in self.graph.edges():
                self.graph[u][v]['weight'] = random.randint(1, 10)
            self.problem = (
                "Найди минимальное остовное дерево для данного графа.\n"
                f"Граф задан ребрами с весами: {[(u, v, self.graph[u][v]['weight']) for u, v in self.graph.edges()]}"
            )
        elif self.task_type == "diameter":
            self.problem = (
                "Найди диаметр данного графа, то есть максимальное расстояние между любыми двумя узлами.\n"
                f"Граф задан ребрами: {list(self.graph.edges())}"
            )
        elif self.task_type == "clustering_coefficient":
            self.problem = (
                "Вычисли средний коэффициент кластеризации данного графа.\n"
                f"Граф задан ребрами: {list(self.graph.edges())}"
            )
        else:
            self.problem = "Неизвестный тип задачи."

    def solve(self):
        self.create_problem_description()
        if self.task_type == "shortest_path":
            try:
                path = nx.shortest_path(self.graph, source=self.start, target=self.end)
                self.solution_steps.append(f"Используем алгоритм Дейкстры для поиска кратчайшего пути: {path}.")
                self.final_answer = str(path)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type == "minimum_spanning_tree":
            try:
                mst = nx.minimum_spanning_tree(self.graph)
                edges = list(mst.edges(data=True))
                self.solution_steps.append(f"Найденное минимальное остовное дерево: {edges}.")
                self.final_answer = str(edges)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type == "diameter":
            try:
                diam = nx.diameter(self.graph)
                self.solution_steps.append(f"Диаметр графа: {diam}.")
                self.final_answer = str(diam)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        elif self.task_type == "clustering_coefficient":
            try:
                avg_coeff = nx.average_clustering(self.graph)
                self.solution_steps.append(f"Средний коэффициент кластеризации: {avg_coeff}.")
                self.final_answer = str(avg_coeff)
            except Exception as e:
                self.solution_steps.append(f"Ошибка: {e}")
                self.final_answer = "Нет решения"
        else:
            self.solution_steps.append("Неизвестный тип задачи.")
            self.final_answer = "Нет решения"

    def generate_prompt(self):
        return f"Задача: {self.problem}\n Пожалуйста, решите задачу пошагово."

    def get_result(self):
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.problem,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }

    @classmethod
    def generate_random_task(cls, only_valid=False, num_nodes=10, edge_prob=0.3):
        task_types = ["shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient"]
        task_type = random.choice(task_types)
        task = cls(task_type=task_type, num_nodes=num_nodes, edge_prob=edge_prob)
        task.solve()
        if only_valid and task.final_answer == "Нет решения":
            return cls.generate_random_task(only_valid=only_valid, num_nodes=num_nodes, edge_prob=edge_prob)
        return task
