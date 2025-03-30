import unittest
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class TestContradictionTask(unittest.TestCase):
    def test_contradiction_ru_large(self):
        """
        Тест задачи противоречий на русском языке с большим количеством утверждений.
        Проверяем, что возвращаются корректные поля:
          - problem содержит нужную строку
          - solution_steps не пуст
          - final_answer не пуст
        """
        task = ContradictionTask(language="ru", num_statements=25)
        result = task.get_result()
    
        # Проверяем наличие всех необходимых полей
        self.assertIn("problem", result, "Результат должен содержать поле 'problem'")
        self.assertIn("solution_steps", result, "Результат должен содержать поле 'solution_steps'")
        self.assertIn("final_answer", result, "Результат должен содержать поле 'final_answer'")
    
        # Проверяем, что в постановке задачи действительно есть фраза "Найдите ложное утверждение" (из prompts.py)
        self.assertIn("Найдите ложное утверждение", result["problem"],
                      "Постановка задачи (problem) должна содержать базовый текст на русском")
    
        # Проверяем, что solution_steps не пуст
        self.assertTrue(len(result["solution_steps"]) > 0,
                       "Поле solution_steps не должно быть пустым")
    
        # Проверяем, что final_answer не пуст
        self.assertTrue(len(result["final_answer"]) > 0,
                       "Поле final_answer не должно быть пустым")
    
        # Проверяем, что в final_answer есть фраза "Ложное утверждение:"
        self.assertIn("Ложное утверждение:", result["final_answer"],
                      "Финальный ответ должен содержать фразу 'Ложное утверждение:'")

    def test_contradiction_en_large(self):
        """
        Тест задачи противоречий на английском языке с большим количеством утверждений.
        Проверяем, что возвращаются корректные поля:
          - problem содержит нужную строку
          - solution_steps не пуст
          - final_answer не пуст
        """
        task = ContradictionTask(language="en", num_statements=25)
        result = task.get_result()
    
        # Проверяем наличие всех необходимых полей
        self.assertIn("problem", result, "Результат должен содержать поле 'problem'")
        self.assertIn("solution_steps", result, "Результат должен содержать поле 'solution_steps'")
        self.assertIn("final_answer", result, "Результат должен содержать поле 'final_answer'")
    
        # Проверяем, что в постановке задачи действительно есть фраза "Find the false statement" (из prompts.py)
        self.assertIn("Find the false statement", result["problem"],
                      "Постановка задачи (problem) должна содержать базовый текст на английском")
    
        # Проверяем, что solution_steps не пуст
        self.assertTrue(len(result["solution_steps"]) > 0,
                       "Поле solution_steps не должно быть пустым")
    
        # Проверяем, что final_answer не пуст
        self.assertTrue(len(result["final_answer"]) > 0,
                       "Поле final_answer не должно быть пустым")
    
        # Проверяем, что в final_answer есть фраза "False statement:"
        self.assertIn("False statement:", result["final_answer"],
                      "Финальный ответ должен содержать фразу 'False statement:'")

if __name__ == '__main__':
    unittest.main()
