import unittest
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class TestContradictionTask(unittest.TestCase):
    def test_contradiction_ru_large(self):
        task = ContradictionTask(language="ru", num_statements=100)
        result = task.get_result()
        # Проверяем, что описание задачи содержит 100 утверждений (каждая строка начинается с "- ")
        lines = result["problem"].split("\n")
        statement_lines = [line for line in lines if line.startswith("- ")]
        self.assertEqual(len(statement_lines), 100, "Должно быть 100 утверждений")
        self.assertIn("Найдите ложное утверждение", result["problem"])
        self.assertIn("Ложное утверждение", result["final_answer"])

    def test_contradiction_en_large(self):
        task = ContradictionTask(language="en", num_statements=100)
        result = task.get_result()
        lines = result["problem"].split("\n")
        statement_lines = [line for line in lines if line.startswith("- ")]
        self.assertEqual(len(statement_lines), 100, "There should be 100 statements")
        self.assertIn("Find the false statement", result["problem"])
        self.assertIn("False statement", result["final_answer"])

if __name__ == '__main__':
    unittest.main()
