import unittest
from re_rl.tasks.math.algebra.linear_task import LinearTask


class TestDetailLevelLinearTask(unittest.TestCase):
    """Тесты на разные уровни детализации для LinearTask."""

    def test_detail_level_1(self):
        """detail_level=1: минимум шагов"""
        task = LinearTask(2, 3, 7, language="ru", detail_level=1)
        task.solve()
        # При detail_level=1 должен быть хотя бы 1 шаг
        self.assertGreaterEqual(len(task.solution_steps), 1)

    def test_detail_level_2(self):
        """detail_level=2: больше шагов"""
        task = LinearTask(2, 3, 7, language="ru", detail_level=2)
        task.solve()
        self.assertGreaterEqual(len(task.solution_steps), 2)

    def test_detail_level_3(self):
        """detail_level=3: полное решение"""
        task = LinearTask(2, 3, 7, language="ru", detail_level=3)
        task.solve()
        self.assertGreaterEqual(len(task.solution_steps), 3)

    def test_detail_level_higher(self):
        """detail_level > 3: не должно ломаться"""
        task = LinearTask(2, 3, 7, language="ru", detail_level=5)
        task.solve()
        # Просто проверяем что работает
        self.assertGreaterEqual(len(task.solution_steps), 1)

    def test_solution_correct(self):
        """Проверка правильности решения"""
        task = LinearTask(2, 3, 7, language="ru", detail_level=3)
        task.solve()
        # 2x + 3 = 7 => x = 2
        self.assertIn("2", task.final_answer)


if __name__ == "__main__":
    unittest.main()
