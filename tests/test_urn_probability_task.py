# tests/test_urn_probability_task.py

import unittest
from re_rl.tasks.math.probability.urn_probability_task import UrnProbabilityTask

class TestUrnProbabilityTask(unittest.TestCase):
    def test_urn_prob_en_all_red(self):
        task = UrnProbabilityTask(language="en", count_containers=2, draws=2)
        res = task.get_result()
        self.assertIn("We have 2", res["problem"])
        self.assertTrue(len(res["solution_steps"]) > 0)
        self.assertIn("The final probability of the event is:", res["final_answer"])

    def test_urn_prob_ru_least_one(self):
        task = UrnProbabilityTask(language="ru", count_containers=3, draws=2)
        res = task.get_result()
        self.assertIn("У нас есть 3", res["problem"])
        self.assertTrue(len(res["solution_steps"]) > 0)
        self.assertIn("Итоговая вероятность события:", res["final_answer"])

if __name__ == "__main__":
    unittest.main()
