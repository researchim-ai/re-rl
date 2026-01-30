import unittest
import sympy as sp
from re_rl.tasks.math.algebra.linear_task import LinearTask
from re_rl.tasks.math.algebra.quadratic_task import QuadraticTask
from re_rl.tasks.math.algebra.cubic_task import CubicTask
from re_rl.tasks.math.algebra.exponential_task import ExponentialTask
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask

class TestLinearTask(unittest.TestCase):
    def test_linear_ru(self):
        task = LinearTask(2, 3, 7, language="ru", augment=False)
        result = task.get_result()
        self.assertIn("Решите линейное уравнение", result["problem"])
        self.assertEqual(result["final_answer"], "2")
        prompt = task.generate_prompt()
        self.assertIn("Решите линейное уравнение", prompt)

    def test_linear_en(self):
        task = LinearTask(2, 3, 7, language="en", augment=False)
        result = task.get_result()
        self.assertIn("Solve the linear equation", result["prompt"])
    
    def test_linear_augmentation(self):
        """Проверяем, что с аугментацией задача создаётся и содержит уравнение."""
        task = LinearTask(2, 3, 7, language="ru", augment=True)
        result = task.get_result()
        # Проверяем, что уравнение присутствует в задаче
        self.assertIn("2x", result["problem"])
        self.assertIn("7", result["problem"])
        self.assertEqual(result["final_answer"], "2")

class TestQuadraticTask(unittest.TestCase):
    def test_quadratic(self):
        task = QuadraticTask(1, -5, 6, language="ru", augment=False)
        result = task.get_result()
        self.assertIn("Решите квадратное уравнение", result["problem"])
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])
    
    def test_quadratic_augmentation(self):
        """Проверяем, что с аугментацией задача создаётся корректно."""
        task = QuadraticTask(1, -5, 6, language="ru", augment=True)
        result = task.get_result()
        # Проверяем, что ответ корректный
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])

class TestCubicTask(unittest.TestCase):
    def test_cubic(self):
        task = CubicTask(1, -6, 11, -6, language="ru", augment=False)
        result = task.get_result()
        self.assertIn("Решите кубическое уравнение", result["problem"])
        for r in [1, 2, 3]:
            self.assertIn(str(r), result["final_answer"])
    
    def test_cubic_augmentation(self):
        """Проверяем, что с аугментацией задача создаётся корректно."""
        task = CubicTask(1, -6, 11, -6, language="ru", augment=True)
        result = task.get_result()
        for r in [1, 2, 3]:
            self.assertIn(str(r), result["final_answer"])

class TestExponentialTask(unittest.TestCase):
    def test_exponential(self):
        task = ExponentialTask(2, 1, 1, 5, language="ru", augment=False)
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)
    
    def test_exponential_augmentation(self):
        """Проверяем, что с аугментацией задача создаётся корректно."""
        task = ExponentialTask(2, 1, 1, 5, language="ru", augment=True)
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

class TestLogarithmicTask(unittest.TestCase):
    def test_logarithmic(self):
        task = LogarithmicTask(2, 3, 1, 5, language="ru", augment=False)
        result = task.get_result()
        expected = sp.exp((5-1)/2) / 3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=2)
    
    def test_logarithmic_augmentation(self):
        """Проверяем, что с аугментацией задача создаётся корректно."""
        task = LogarithmicTask(2, 3, 1, 5, language="ru", augment=True)
        result = task.get_result()
        expected = sp.exp((5-1)/2) / 3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=2)

if __name__ == '__main__':
    unittest.main()
