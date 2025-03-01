import unittest
import sympy as sp
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.system_linear_task import SystemLinearTask
from re_rl.tasks.analogical_task import AnalogicalTask
from re_rl.tasks.factory import MathTaskFactory
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class TestLinearTask(unittest.TestCase):
    def test_linear_ru(self):
        task = LinearTask(2, 3, 7, language="ru", detail_level=4)
        result = task.get_result()
        self.assertIn("Решите линейное уравнение", result["problem"])
        self.assertEqual(result["final_answer"], "2")
        self.assertTrue(result["prompt"].startswith("Задача:"))

    def test_linear_en(self):
        task = LinearTask(2, 3, 7, language="en", detail_level=4)
        result = task.get_result()
        self.assertIn("Solve the linear equation", result["problem"])
        self.assertEqual(result["final_answer"], "2")
        self.assertTrue(result["prompt"].startswith("Task:"))

class TestQuadraticTask(unittest.TestCase):
    def test_quadratic(self):
        task = QuadraticTask(1, -5, 6, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("Решите квадратное уравнение", result["problem"])
        self.assertTrue("2" in result["final_answer"] or "3" in result["final_answer"])

class TestCubicTask(unittest.TestCase):
    def test_cubic(self):
        task = CubicTask(1, -6, 11, -6, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("Решите кубическое уравнение", result["problem"])
        for r in ["1", "2", "3"]:
            self.assertIn(r, result["final_answer"])

class TestExponentialTask(unittest.TestCase):
    def test_exponential(self):
        task = ExponentialTask(2, 1, 1, 5, language="en", detail_level=4)
        result = task.get_result()
        expected = sp.log(2)
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

class TestLogarithmicTask(unittest.TestCase):
    def test_logarithmic(self):
        task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=3)
        result = task.get_result()
        expected = sp.exp((5-1)/2)/3
        self.assertAlmostEqual(float(result["final_answer"]), float(expected), places=5)

class TestCalculusTask(unittest.TestCase):
    def test_differentiation(self):
        task = CalculusTask("differentiation", degree=2, language="ru", detail_level=3)
        result = task.get_result()
        self.assertIn("производную", result["problem"])
        self.assertNotEqual(result["final_answer"].strip(), "")

    def test_integration(self):
        task = CalculusTask("integration", degree=2, language="en", detail_level=3)
        result = task.get_result()
        self.assertIn("indefinite integral", result["problem"])
        self.assertNotEqual(result["final_answer"].strip(), "")

class TestSystemLinearTask(unittest.TestCase):
    def test_system_linear(self):
        matrix = [
            [2, 1, 5],
            [1, 2, 4]
        ]
        task = SystemLinearTask(matrix, language="ru", detail_level=4)
        result = task.get_result()
        self.assertIn("Решите систему уравнений", result["problem"])
        self.assertIn("x1 = 2.00", result["final_answer"])
        self.assertIn("x2 = 1.00", result["final_answer"])

class TestAnalogicalTask(unittest.TestCase):
    def test_analogical_en(self):
        description = ("In biology, scientists use the structure of the human eye to understand how cameras work. "
                       "How might this analogy be used to solve a problem with a malfunctioning camera?")
        task = AnalogicalTask(description, language="en", detail_level=4)
        result = task.get_result()
        # Ожидаем, что prompt начинается с "Using analogy" или "Using analogy, solve the following problem:"
        self.assertTrue(result["prompt"].startswith("Using analogy"))
        self.assertEqual(len(result["solution_steps"]), 4)
        self.assertIn("An analogical solution", result["final_answer"])

class TestGraphTask(unittest.TestCase):
    def test_graph_ru(self):
        # Используем параметры, которые повышают вероятность получения корректного решения
        task = GraphTask.generate_random_task(only_valid=True, num_nodes=15, edge_prob=0.3, language="ru", detail_level=3)
        result = task.get_result()
        # Допустимые варианты промта: либо стандартный из default, либо другой, если задача не математическая
        self.assertTrue(result["prompt"].startswith("Задача:") or result["prompt"].startswith("Используя аналогию"))
        self.assertNotEqual(result["final_answer"], PROMPT_TEMPLATES["default"]["no_solution"]["ru"])



class TestFactory(unittest.TestCase):
    def test_factory_math(self):
        task = MathTaskFactory.generate_random_math_task(only_valid=True, language="en", detail_level=3)
        result = task.get_result()
        self.assertTrue(result["prompt"].startswith("Task:"))
        self.assertNotEqual(result["final_answer"], PROMPT_TEMPLATES["default"]["no_solution"]["en"])
    
    def test_factory_all(self):
        task = MathTaskFactory.generate_random_task(only_valid=True, language="ru", detail_level=3)
        result = task.get_result()
        # Допускаем, что промт может начинаться с "Задача:" или "Используя аналогию"
        self.assertTrue(result["prompt"].startswith("Задача:") or result["prompt"].startswith("Используя аналогию"))
        self.assertNotEqual(result["final_answer"], PROMPT_TEMPLATES["default"]["no_solution"]["ru"])
    
    def test_language_switch(self):
        task_ru = LinearTask(2, 3, 7, language="ru", detail_level=3)
        task_en = LinearTask(2, 3, 7, language="en", detail_level=3)
        prompt_ru = task_ru.generate_prompt()
        prompt_en = task_en.generate_prompt()
        self.assertNotEqual(prompt_ru, prompt_en)
        self.assertIn("Решите", prompt_ru)
        self.assertIn("Solve", prompt_en)

if __name__ == '__main__':
    unittest.main()
