import unittest
from re_rl.tasks.linear_task import LinearTask

class TestDetailLevelLinearTask(unittest.TestCase):
    def test_detail_level_1(self):
        # При detail_level = 1 ожидается 1 шаг (только шаг 1)
        task = LinearTask(2, 3, 7, language="ru", detail_level=1)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 1, "При detail_level=1 ожидается 1 шаг")
        self.assertIn("Записываем уравнение", result["solution_steps"][0])
    
    def test_detail_level_2(self):
        # При detail_level = 2 ожидается 2 шага (шаги 1 и 2)
        task = LinearTask(2, 3, 7, language="ru", detail_level=2)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 2, "При detail_level=2 ожидается 2 шага")
        self.assertIn("Записываем уравнение", result["solution_steps"][0])
        self.assertIn("Анализируем уравнение", result["solution_steps"][1])
    
    def test_detail_level_3(self):
        # При detail_level = 3 ожидается 3 шага (шаги 1, 2 и 3)
        task = LinearTask(2, 3, 7, language="ru", detail_level=3)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 3, "При detail_level=3 ожидается 3 шага")
        self.assertIn("Записываем уравнение", result["solution_steps"][0])
        self.assertIn("Анализируем уравнение", result["solution_steps"][1])
        self.assertIn("Переносим свободный член", result["solution_steps"][2])
    
    def test_detail_level_5(self):
        # При detail_level = 5 ожидается 5 шагов
        task = LinearTask(2, 3, 7, language="ru", detail_level=5)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 5, "При detail_level=5 ожидается 5 шагов")
        self.assertIn("Записываем уравнение", result["solution_steps"][0])
        self.assertIn("Анализируем уравнение", result["solution_steps"][1])
        self.assertIn("Переносим свободный член", result["solution_steps"][2])
        self.assertIn("Делим обе части", result["solution_steps"][3])
        self.assertIn("Решаем уравнение", result["solution_steps"][4])

if __name__ == '__main__':
    unittest.main()
