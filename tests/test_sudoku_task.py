# tests/test_sudoku_task.py
import unittest
from re_rl.tasks.math.logic.sudoku_task import SudokuTask


class TestSudokuTask(unittest.TestCase):
    """Тесты для SudokuTask."""
    
    def test_sudoku_4x4_ru(self):
        """Тест судоку 4x4 на русском."""
        task = SudokuTask(language="ru", difficulty=2, detail_level=3)
        result = task.get_result()
        
        self.assertIn("судоку", result["problem"].lower())
        self.assertEqual(task.size, 4)
        self.assertEqual(task.block_size, 2)
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_sudoku_4x4_en(self):
        """Тест судоку 4x4 на английском."""
        task = SudokuTask(language="en", difficulty=2, detail_level=3)
        result = task.get_result()
        
        self.assertIn("Sudoku", result["problem"])
        self.assertEqual(task.size, 4)
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_sudoku_9x9_ru(self):
        """Тест судоку 9x9 на русском."""
        task = SudokuTask(language="ru", difficulty=6, detail_level=5)
        result = task.get_result()
        
        self.assertEqual(task.size, 9)
        self.assertEqual(task.block_size, 3)
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_sudoku_solution_valid(self):
        """Проверка валидности решения судоку."""
        task = SudokuTask(language="ru", difficulty=3)
        
        # Проверяем, что решение заполнено
        self.assertIsNotNone(task.solution)
        self.assertEqual(len(task.solution), task.size)
        
        # Проверяем уникальность в строках
        for row in task.solution:
            self.assertEqual(len(set(row)), task.size)
        
        # Проверяем уникальность в столбцах
        for col in range(task.size):
            column = [task.solution[row][col] for row in range(task.size)]
            self.assertEqual(len(set(column)), task.size)
    
    def test_sudoku_difficulty_presets(self):
        """Тест пресетов сложности."""
        # Лёгкая сложность - 4x4
        task_easy = SudokuTask(difficulty=1)
        self.assertEqual(task_easy.size, 4)
        
        # Средняя сложность - 9x9
        task_medium = SudokuTask(difficulty=5)
        self.assertEqual(task_medium.size, 9)
        
        # Высокая сложность - 9x9 с меньшим количеством подсказок
        task_hard = SudokuTask(difficulty=10)
        self.assertEqual(task_hard.size, 9)
        self.assertLess(task_hard.hints_ratio, task_medium.hints_ratio)
    
    def test_sudoku_puzzle_has_empty_cells(self):
        """Проверка, что в пазле есть пустые клетки."""
        task = SudokuTask(difficulty=5)
        
        empty_count = sum(1 for row in task.puzzle for cell in row if cell is None)
        self.assertGreater(empty_count, 0)
    
    def test_sudoku_get_task_type(self):
        """Тест типа задачи."""
        task = SudokuTask()
        self.assertEqual(task.get_task_type(), "sudoku")


if __name__ == '__main__':
    unittest.main()
