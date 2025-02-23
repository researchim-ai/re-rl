import unittest
import sympy as sp
from re_rl.tasks.calculus_task import CalculusTask

# Вспомогательные классы для фиксированной функции f(x) = 3*x**2 + 2*x + 1,
# чтобы можно было сравнить ожидаемые результаты.
class FixedCalculusTaskDifferentiation(CalculusTask):
    def generate_function(self):
        x = sp.symbols('x')
        # Фиксированная функция: 3*x**2 + 2*x + 1
        self.function = 3*x**2 + 2*x + 1

class FixedCalculusTaskIntegration(CalculusTask):
    def generate_function(self):
        x = sp.symbols('x')
        # Фиксированная функция: 3*x**2 + 2*x + 1
        self.function = 3*x**2 + 2*x + 1

class TestCalculusTask(unittest.TestCase):
    def test_differentiation(self):
        # Для f(x) = 3*x**2 + 2*x + 1, производная должна быть 6*x + 2
        task = FixedCalculusTaskDifferentiation(task_type="differentiation", degree=2)
        result = task.get_result()
        x = sp.symbols('x')
        expected = sp.diff(3*x**2 + 2*x + 1, x)  # 6*x + 2
        self.assertEqual(result["final_answer"], sp.pretty(expected))
        combined_steps = " ".join(result["solution_steps"]).lower()
        self.assertTrue("производную" in combined_steps or "вычисляем" in combined_steps)

    def test_integration(self):
        # Для f(x) = 3*x**2 + 2*x + 1, неопределённый интеграл равен x**3 + x**2 + x + C
        task = FixedCalculusTaskIntegration(task_type="integration", degree=2)
        result = task.get_result()
        x = sp.symbols('x')
        expected = sp.integrate(3*x**2 + 2*x + 1, x)  # x**3 + x**2 + x
        self.assertEqual(result["final_answer"], sp.pretty(expected) + " + C")
        combined_steps = " ".join(result["solution_steps"]).lower()
        self.assertIn("интеграл", combined_steps)

    def test_generate_random_task(self):
        # Проверяем, что метод generate_random_task возвращает задачу с непустым ответом
        task = CalculusTask.generate_random_task(task_type="differentiation")
        result = task.get_result()
        self.assertIsNotNone(result["final_answer"])
        self.assertNotEqual(result["final_answer"].strip(), "")

if __name__ == '__main__':
    unittest.main()
