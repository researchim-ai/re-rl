import unittest
from re_rl.tasks.linear_task import LinearTask

class TestDetailLevelLinearTask(unittest.TestCase):
    def test_detail_level_1(self):
        # При detail_level = 1 ожидается 1 шаг (только шаг 1)
        task = LinearTask(2, 3, 7, language="ru", detail_level=1)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 1, "При detail_level=1 ожидается 1 шаг")
        self.assertEqual(len(result["explanations"]), 1, "При detail_level=1 ожидается 1 объяснение")
        self.assertEqual(len(result["validations"]), 1, "При detail_level=1 ожидается 1 валидация")
    
    def test_detail_level_2(self):
        # При detail_level = 2 ожидается 2 шага (шаги 1 и 2)
        task = LinearTask(2, 3, 7, language="ru", detail_level=2)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 2, "При detail_level=2 ожидается 2 шага")
        self.assertEqual(len(result["explanations"]), 2, "При detail_level=2 ожидается 2 объяснения")
        self.assertEqual(len(result["validations"]), 2, "При detail_level=2 ожидается 2 валидации")
    
    def test_detail_level_3(self):
        # При detail_level = 3 ожидается 3 шага (шаги 1, 2 и 3)
        task = LinearTask(2, 3, 7, language="ru", detail_level=3)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 3, "При detail_level=3 ожидается 3 шага")
        self.assertEqual(len(result["explanations"]), 3, "При detail_level=3 ожидается 3 объяснения")
        self.assertEqual(len(result["validations"]), 3, "При detail_level=3 ожидается 3 валидации")
    
    def test_detail_level_5(self):
        # При detail_level = 5: 1 (шаг 1) + 1 (шаг 2) + (2 дополнительных шага + шаг 3) = 5 шагов
        task = LinearTask(2, 3, 7, language="ru", detail_level=5)
        result = task.get_result()
        self.assertEqual(len(result["solution_steps"]), 5, "При detail_level=5 ожидается 5 шагов")
        self.assertEqual(len(result["explanations"]), 5, "При detail_level=5 ожидается 5 объяснений")
        self.assertEqual(len(result["validations"]), 5, "При detail_level=5 ожидается 5 валидаций")
        
        # Проверяем содержание шагов
        self.assertIn("Записываем уравнение", result["explanations"][0])
        self.assertIn("Вычисляем правую часть", result["explanations"][1])
        self.assertIn("Разбиваем", result["explanations"][2])
        self.assertIn("Проверяем сумму", result["explanations"][3])
        self.assertIn("Делим правую часть", result["explanations"][4])
        
        # Проверяем валидации
        self.assertIn("Уравнение записано корректно", result["validations"][0])
        self.assertIn("Правая часть равна", result["validations"][1])
        self.assertIn("Части:", result["validations"][2])
        self.assertIn("Сумма частей равна", result["validations"][3])
        self.assertIn("Решение:", result["validations"][4])

if __name__ == '__main__':
    unittest.main()
