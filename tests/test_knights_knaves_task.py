import unittest
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask

class TestKnightsKnavesTask(unittest.TestCase):
    def test_knights_knaves_ru(self):
        """
        Тест задачи Knights & Knaves на русском языке с detail_level=5.
        Проверяем, что возвращаются корректные поля:
          - problem содержит нужную строку
          - solution_steps не пуст
          - final_answer не пуст
        """
        task = KnightsKnavesTask(language="ru", detail_level=5)
        result = task.get_result()
        
        # Проверяем, что в постановке задачи действительно есть фраза "У нас есть три персонажа" (из prompts.py)
        self.assertIn("У нас есть три персонажа", result["problem"], 
                      "Постановка задачи (problem) должна содержать базовый текст на русском")
        
        # Проверяем, что итоги решения не пустые
        self.assertTrue(result["solution_steps"], "solution_steps не должен быть пустым")
        self.assertTrue(result["final_answer"], "final_answer не должен быть пустым")
        
        # Дополнительно можем проверить длину solution_steps
        self.assertLessEqual(len(result["solution_steps"]), 5, "Число шагов не должно превышать detail_level=5")

    def test_knights_knaves_en(self):
        """
        Тест задачи Knights & Knaves на английском языке с detail_level=3.
        """
        task = KnightsKnavesTask(language="en", detail_level=3)
        result = task.get_result()
        
        # Проверяем, что постановка задачи содержит английский текст
        self.assertIn("We have three characters", result["problem"], 
                      "Постановка задачи (problem) должна содержать базовый текст на английском")
        
        # Проверяем наличие финального ответа
        self.assertTrue(result["final_answer"], "final_answer не должен быть пустым")
        
        # Проверяем, что есть ровно 3 шага (по detail_level=3)
        self.assertEqual(len(result["solution_steps"]), 3, 
                         "Число шагов должно соответствовать detail_level=3")

if __name__ == '__main__':
    unittest.main()
