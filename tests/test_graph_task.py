import unittest
from re_rl.tasks.graph_task import GraphTask
import networkx as nx

class TestGraphTask(unittest.TestCase):
    def test_shortest_path(self):
        task = GraphTask(task_type="shortest_path", num_nodes=10, edge_prob=0.5)
        task.solve()
        result = task.get_result()
        self.assertIn("Найди кратчайший путь", result["problem"])
        self.assertNotEqual(result["final_answer"], "Нет решения")
        # Проверяем, что ответ выглядит как список узлов
        self.assertTrue(result["final_answer"].startswith('[') and result["final_answer"].endswith(']'))

    def test_minimum_spanning_tree(self):
        task = GraphTask(task_type="minimum_spanning_tree", num_nodes=10, edge_prob=0.5)
        task.solve()
        result = task.get_result()
        self.assertIn("минимальное остовное дерево", result["problem"])
        self.assertNotEqual(result["final_answer"], "Нет решения")
        self.assertIn("weight", result["final_answer"])

    def test_diameter(self):
        task = GraphTask(task_type="diameter", num_nodes=10, edge_prob=0.5)
        task.solve()
        result = task.get_result()
        # Обычно в шагах решения появляется слово "Диаметр"
        self.assertTrue(any("Диаметр" in step for step in result["solution_steps"]))
        self.assertNotEqual(result["final_answer"], "Нет решения")
        try:
            val = int(result["final_answer"])
        except ValueError:
            self.fail("Итоговый ответ для диаметра не является целым числом")

    def test_clustering_coefficient(self):
        task = GraphTask(task_type="clustering_coefficient", num_nodes=10, edge_prob=0.5)
        task.solve()
        result = task.get_result()
        # Проверяем, что в решении упоминается коэффициент кластеризации
        self.assertTrue(any("коэффициент кластеризации" in step for step in result["solution_steps"]))
        self.assertNotEqual(result["final_answer"], "Нет решения")
        try:
            val = float(result["final_answer"])
        except ValueError:
            self.fail("Итоговый ответ для среднего коэффициента кластеризации не является числом")

    def test_generate_random_task_valid(self):
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=10, edge_prob=0.5)
        result = task.get_result()
        self.assertNotEqual(result["final_answer"], "Нет решения")
        self.assertIn(task.task_type, ["shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient"])

if __name__ == '__main__':
    unittest.main()
