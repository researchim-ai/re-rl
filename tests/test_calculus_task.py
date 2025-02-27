import unittest
from re_rl.tasks.calculus_task import CalculusTask

class TestCalculusTask(unittest.TestCase):
    def test_differentiation(self):
        task = CalculusTask("differentiation", degree=2, language="ru")
        result = task.get_result()
        self.assertNotEqual(result["final_answer"].strip(), "")

    def test_integration(self):
        task = CalculusTask("integration", degree=2, language="en")
        result = task.get_result()
        self.assertNotEqual(result["final_answer"].strip(), "")

if __name__ == '__main__':
    unittest.main()
