# tests/test_zebra_puzzle_task.py
import unittest
from re_rl.tasks.math.logic.zebra_puzzle_task import ZebraPuzzleTask


class TestZebraPuzzleTask(unittest.TestCase):
    """Тесты для ZebraPuzzleTask."""
    
    def test_zebra_puzzle_ru(self):
        """Тест загадки Эйнштейна на русском."""
        task = ZebraPuzzleTask(language="ru", difficulty=3, detail_level=3)
        result = task.get_result()
        
        self.assertIn("дом", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
        self.assertIsNotNone(task.answer)
    
    def test_zebra_puzzle_en(self):
        """Тест загадки Эйнштейна на английском."""
        task = ZebraPuzzleTask(language="en", difficulty=3, detail_level=3)
        result = task.get_result()
        
        self.assertIn("house", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_zebra_puzzle_difficulty_scaling(self):
        """Тест масштабирования сложности."""
        task_easy = ZebraPuzzleTask(difficulty=1)
        task_hard = ZebraPuzzleTask(difficulty=10)
        
        # Сложная задача должна иметь больше домов/категорий
        self.assertLessEqual(task_easy.num_houses, task_hard.num_houses)
        self.assertLessEqual(task_easy.num_categories, task_hard.num_categories)
    
    def test_zebra_puzzle_solution_structure(self):
        """Проверка структуры решения."""
        task = ZebraPuzzleTask(difficulty=3)
        
        # Решение должно содержать все категории
        for category in task.categories:
            self.assertIn(category, task.solution)
            self.assertEqual(len(task.solution[category]), task.num_houses)
    
    def test_zebra_puzzle_clues_generated(self):
        """Проверка генерации подсказок."""
        task = ZebraPuzzleTask(difficulty=5)
        
        self.assertGreater(len(task.clues), 0)
        for clue in task.clues:
            self.assertIn("text", clue)
            self.assertIn("type", clue)
    
    def test_zebra_puzzle_question_and_answer(self):
        """Проверка вопроса и ответа."""
        task = ZebraPuzzleTask(difficulty=5)
        
        self.assertIsNotNone(task.question)
        self.assertIsNotNone(task.answer)
        self.assertGreater(len(task.question), 0)
        self.assertGreater(len(task.answer), 0)
    
    def test_zebra_puzzle_get_task_type(self):
        """Тест типа задачи."""
        task = ZebraPuzzleTask()
        self.assertEqual(task.get_task_type(), "zebra_puzzle")


if __name__ == '__main__':
    unittest.main()
