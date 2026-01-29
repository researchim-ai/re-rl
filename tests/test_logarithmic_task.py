import unittest
import math
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask


class TestLogarithmicTask(unittest.TestCase):
    """Тесты для LogarithmicTask."""

    def test_logarithmic_task_ru(self):
        """Проверка генерации задачи на русском"""
        task = LogarithmicTask(a=2, b=3, c=1, d=5, language="ru")
        task.solve()
        
        self.assertIn("Решите логарифмическое уравнение", task.description)
        self.assertGreater(len(task.solution_steps), 0)
        self.assertIsNotNone(task.final_answer)

    def test_logarithmic_task_en(self):
        """Проверка генерации задачи на английском"""
        task = LogarithmicTask(a=2, b=3, c=1, d=5, language="en")
        task.solve()
        
        self.assertIn("Solve the logarithmic equation", task.description)
        self.assertGreater(len(task.solution_steps), 0)

    def test_logarithmic_task_solution(self):
        """Проверка корректности решения"""
        # a*log(b*x) + c = d
        # 2*log(3*x) + 1 = 5
        a, b, c, d = 2, 3, 1, 5
        task = LogarithmicTask(a=a, b=b, c=c, d=d, language="ru")
        task.solve()
        
        # Извлекаем ответ
        answer_str = task.final_answer.replace(",", ".")
        # Убираем форматирование
        for char in ["$", "x", "=", " "]:
            answer_str = answer_str.replace(char, "")
        
        x = float(answer_str)
        
        # Проверяем: a*log(b*x) + c должно быть близко к d
        result = a * math.log(b * x) + c
        self.assertAlmostEqual(result, d, places=2)

    def test_logarithmic_latex_format(self):
        """Проверка LaTeX формата"""
        task = LogarithmicTask(a=2, b=3, c=1, d=5, language="ru", output_format="latex")
        task.solve()
        
        # LaTeX должен содержать $ символы
        self.assertIn("$", task.description)

    def test_logarithmic_difficulty_levels(self):
        """Проверка разных уровней сложности"""
        for difficulty in [1, 5, 10]:
            task = LogarithmicTask(difficulty=difficulty, language="ru")
            task.solve()
            self.assertGreater(len(task.solution_steps), 0)


if __name__ == "__main__":
    unittest.main()
