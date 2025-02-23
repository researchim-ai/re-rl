import unittest
import sympy as sp
from re_rl.tasks.math_task import MathTask

class TestMathTask(unittest.TestCase):
    def test_linear_equation(self):
        # 2x + 3 = 7  -> x = 2
        task = MathTask("linear", 2, 3, 7)
        result = task.get_result()
        self.assertEqual(result["final_answer"], "2")
        self.assertIn("Решите линейное уравнение", result["problem"])
        self.assertGreater(len(result["solution_steps"]), 0)

    def test_quadratic_equation(self):
        # x^2 - 5x + 6 = 0 -> решения: 2 и 3
        task = MathTask("quadratic", 1, -5, 6)
        result = task.get_result()
        self.assertIn("Решите квадратное уравнение", result["problem"])
        # Проверяем, что итоговый ответ содержит хотя бы одно из ожидаемых чисел
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])

    def test_cubic_equation(self):
        # x^3 - 6x^2 + 11x - 6 = 0 -> корни: 1, 2, 3
        task = MathTask("cubic", 1, -6, 11, -6)
        result = task.get_result()
        self.assertIn("Решите кубическое уравнение", result["problem"])
        for root in ["1", "2", "3"]:
            self.assertIn(root, result["final_answer"])

    def test_exponential_equation(self):
        # 2*exp(x) + 1 = 5 -> exp(x) = 2 -> x = ln(2)
        task = MathTask("exponential", 2, 1, 1, 5)
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

    def test_logarithmic_equation(self):
        # 2*log(3*x) + 1 = 5 -> x = exp((5-1)/2)/3 = exp(2)/3
        task = MathTask("logarithmic", 2, 3, 1, 5)
        result = task.get_result()
        expected = sp.exp((5 - 1) / 2) / 3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

    def test_generate_random_task_valid(self):
        # Проверяем генерацию задачи, которая гарантированно решаема, если only_valid=True.
        task = MathTask.generate_random_task(only_valid=True)
        result = task.get_result()
        self.assertNotEqual(result["final_answer"], "Нет решений")

if __name__ == "__main__":
    unittest.main()
