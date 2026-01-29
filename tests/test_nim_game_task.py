# tests/test_nim_game_task.py
import unittest
from functools import reduce
from operator import xor
from re_rl.tasks.math.discrete.nim_game_task import NimGameTask


class TestNimGameTask(unittest.TestCase):
    """Тесты для NimGameTask."""
    
    def test_nim_game_ru(self):
        """Тест игры Ним на русском."""
        task = NimGameTask(language="ru", difficulty=3, detail_level=5)
        result = task.get_result()
        
        self.assertIn("ним", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_nim_game_en(self):
        """Тест игры Ним на английском."""
        task = NimGameTask(language="en", difficulty=3, detail_level=5)
        result = task.get_result()
        
        self.assertIn("nim", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_nim_sum_computation(self):
        """Проверка вычисления ним-суммы."""
        # Известные случаи
        task = NimGameTask(piles=[1, 2, 3])
        self.assertEqual(task.nim_sum, 1 ^ 2 ^ 3)  # = 0
        
        task = NimGameTask(piles=[3, 4, 5])
        self.assertEqual(task.nim_sum, 3 ^ 4 ^ 5)  # = 2
    
    def test_nim_winning_position(self):
        """Тест выигрышной позиции (ним-сумма != 0)."""
        task = NimGameTask(piles=[3, 4, 5])
        
        self.assertNotEqual(task.nim_sum, 0)
        self.assertIsNotNone(task.winning_move)
    
    def test_nim_losing_position(self):
        """Тест проигрышной позиции (ним-сумма = 0)."""
        task = NimGameTask(piles=[1, 2, 3])
        
        self.assertEqual(task.nim_sum, 0)
        self.assertIsNone(task.winning_move)
    
    def test_nim_winning_move_valid(self):
        """Проверка корректности выигрышного хода."""
        task = NimGameTask(piles=[3, 4, 5])
        
        if task.winning_move:
            pile_idx, take, new_size = task.winning_move
            
            # Проверяем, что ход валиден
            self.assertGreaterEqual(pile_idx, 0)
            self.assertLess(pile_idx, len(task.piles))
            self.assertGreater(take, 0)
            self.assertLessEqual(take, task.piles[pile_idx])
            self.assertEqual(new_size, task.piles[pile_idx] - take)
            
            # Проверяем, что после хода ним-сумма = 0
            new_piles = task.piles.copy()
            new_piles[pile_idx] = new_size
            new_nim_sum = reduce(xor, new_piles, 0)
            self.assertEqual(new_nim_sum, 0)
    
    def test_nim_difficulty_scaling(self):
        """Тест масштабирования сложности."""
        task_easy = NimGameTask(difficulty=1)
        task_hard = NimGameTask(difficulty=10)
        
        # Сложная задача имеет больше кучек или большие числа
        self.assertLessEqual(len(task_easy.piles), len(task_hard.piles))
    
    def test_nim_custom_piles(self):
        """Тест с заданными кучками."""
        piles = [7, 11, 13]
        task = NimGameTask(piles=piles)
        
        self.assertEqual(task.piles, piles)
        self.assertEqual(task.nim_sum, 7 ^ 11 ^ 13)
    
    def test_nim_get_task_type(self):
        """Тест типа задачи."""
        task = NimGameTask()
        self.assertEqual(task.get_task_type(), "nim_game")
    
    def test_nim_single_pile(self):
        """Тест с одной кучкой."""
        task = NimGameTask(piles=[5])
        
        # С одной кучкой первый игрок всегда выигрывает (берёт всё кроме одного)
        self.assertNotEqual(task.nim_sum, 0)
        self.assertIsNotNone(task.winning_move)


if __name__ == '__main__':
    unittest.main()
