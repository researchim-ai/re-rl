import unittest
from re_rl.tasks.math.discrete.graph_task import GraphTask

class TestGraphTask(unittest.TestCase):
    def test_graph(self):
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=10, edge_prob=0.5, language="ru")
        result = task.get_result()
        self.assertIn("Найди", result["problem"])
        self.assertNotEqual(result["final_answer"], "Нет решения")

if __name__ == '__main__':
    unittest.main()
