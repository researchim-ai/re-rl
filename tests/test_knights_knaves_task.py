import unittest
from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask

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
        
        # Проверяем, что в постановке задачи действительно есть фраза "У нас есть три персонажей" (из prompts.py)
        self.assertIn("У нас есть три персонажей", result["problem"],
                      "Постановка задачи (problem) должна содержать базовый текст на русском")
        self.assertIn("говорит:", result["problem"],
                      "Постановка задачи должна содержать высказывания персонажей")
        self.assertIn("Определите, кто из них рыцарь, а кто — лжец", result["problem"],
                      "Постановка задачи должна содержать инструкцию по решению")
        
        # Проверяем, что solution_steps не пуст
        self.assertTrue(len(result["solution_steps"]) > 0,
                       "Поле solution_steps не должно быть пустым")
        
        # Проверяем, что final_answer не пуст
        self.assertTrue(len(result["final_answer"]) > 0,
                       "Поле final_answer не должно быть пустым")
        
        # Проверяем что есть достаточно шагов для подробного решения
        self.assertGreater(len(result["solution_steps"]), 0, "Должны быть шаги решения")

    def test_knights_knaves_en(self):
        """
        Тест задачи Knights & Knaves на английском языке с detail_level=3.
        """
        task = KnightsKnavesTask(language="en", detail_level=3)
        result = task.get_result()
        
        # Проверяем, что постановка задачи содержит английский текст
        self.assertIn("We have three characters", result["problem"], 
                      "Постановка задачи (problem) должна содержать базовый текст на английском")
        self.assertIn("says:", result["problem"],
                      "Постановка задачи должна содержать высказывания персонажей")
        self.assertIn("Determine who is a knight and who is a knave", result["problem"],
                      "Постановка задачи должна содержать инструкцию по решению")
        
        # Проверяем наличие финального ответа
        self.assertTrue(result["final_answer"], "final_answer не должен быть пустым")
        
        # Проверяем, что есть шаги решения (detail_level больше не обрезает шаги)
        self.assertTrue(len(result["solution_steps"]) > 0, 
                         "Должны быть шаги решения")

if __name__ == '__main__':
    unittest.main()
