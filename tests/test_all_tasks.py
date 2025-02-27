import unittest
import sympy as sp
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.factory import MathTaskFactory

class TestLinearTask(unittest.TestCase):
    def test_linear_ru(self):
        # Пример: 2x + 3 = 7 -> x = 2
        task = LinearTask(2, 3, 7, language="ru")
        result = task.get_result()
        self.assertIn("Решите линейное уравнение", result["prompt"])
        self.assertEqual(result["final_answer"], "2")
        latex_sol = task.generate_latex_solution()
        self.assertTrue(latex_sol.startswith(r"\begin{align*}"))
    
    def test_linear_en(self):
        task = LinearTask(2, 3, 7, language="en")
        result = task.get_result()
        self.assertIn("Solve the linear equation", result["prompt"])
        # Проверка, что промт различается от русского
        self.assertNotEqual(task.generate_prompt(), LinearTask(2, 3, 7, language="ru").generate_prompt())

class TestQuadraticTask(unittest.TestCase):
    def test_quadratic_ru(self):
        task = QuadraticTask(1, -5, 6, language="ru")
        result = task.get_result()
        self.assertIn("Решите квадратное уравнение", result["prompt"])
        # Корни уравнения x^2 - 5x + 6 = 0 должны быть 2 и 3
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])
    
    def test_quadratic_en(self):
        task = QuadraticTask(1, -5, 6, language="en")
        prompt = task.generate_prompt()
        self.assertIn("Solve the quadratic equation", prompt)

class TestCubicTask(unittest.TestCase):
    def test_cubic(self):
        task = CubicTask(1, -6, 11, -6, language="en")
        result = task.get_result()
        self.assertIn("Solve the cubic equation", result["prompt"])
        # Проверка, что все ожидаемые корни присутствуют
        for r in ["1", "2", "3"]:
            self.assertIn(r, result["final_answer"])
        latex_sol = task.generate_latex_solution()
        self.assertTrue(latex_sol.startswith(r"\begin{align*}"))

class TestExponentialTask(unittest.TestCase):
    def test_exponential(self):
        task = ExponentialTask(2, 1, 1, 5, language="en")
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

class TestLogarithmicTask(unittest.TestCase):
    def test_logarithmic(self):
        task = LogarithmicTask(2, 3, 1, 5, language="ru")
        result = task.get_result()
        expected = sp.exp((5-1)/2)/3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

class TestCalculusTask(unittest.TestCase):
    def test_differentiation_ru(self):
        task = CalculusTask("differentiation", degree=2, language="ru")
        result = task.get_result()
        self.assertIn("Найди производную", result["prompt"])
        self.assertNotEqual(result["final_answer"].strip(), "")
    
    def test_integration_en(self):
        task = CalculusTask("integration", degree=2, language="en")
        result = task.get_result()
        self.assertIn("Find the", result["prompt"])
        self.assertNotEqual(result["final_answer"].strip(), "")
    
class TestGraphTask(unittest.TestCase):
    def test_graph_ru(self):
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=10, edge_prob=0.5, language="ru")
        result = task.get_result()
        self.assertIn("Найди", result["prompt"])
        self.assertNotEqual(result["final_answer"], "Нет решения")
    
    def test_graph_en(self):
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=10, edge_prob=0.5, language="en")
        prompt = task.generate_prompt()
        self.assertIn("Find", prompt)

class TestFactory(unittest.TestCase):
    def test_factory_math(self):
        task = MathTaskFactory.generate_random_math_task(only_valid=True, language="en")
        result = task.get_result()
        self.assertIn("Solve", result["prompt"])
        self.assertNotEqual(result["final_answer"], "Нет решений")
    
    def test_factory_all(self):
        task = MathTaskFactory.generate_random_task(only_valid=True, language="ru")
        result = task.get_result()
        self.assertIn("Задача:", result["prompt"])
        self.assertNotEqual(result["final_answer"], "Нет решения")
    
    def test_language_switch(self):
        # Тот же набор параметров, но разный язык, должны отличаться
        task_ru = LinearTask(2, 3, 7, language="ru")
        task_en = LinearTask(2, 3, 7, language="en")
        prompt_ru = task_ru.generate_prompt()
        prompt_en = task_en.generate_prompt()
        self.assertNotEqual(prompt_ru, prompt_en)
        self.assertIn("Решите", prompt_ru)
        self.assertIn("Solve", prompt_en)

if __name__ == '__main__':
    unittest.main()
