# tests/test_tower_of_hanoi_task.py
import unittest
from re_rl.tasks.math.planning.tower_of_hanoi_task import TowerOfHanoiTask


class TestTowerOfHanoiTask(unittest.TestCase):
    """Тесты для TowerOfHanoiTask."""
    
    def test_hanoi_ru(self):
        """Тест Ханойской башни на русском."""
        task = TowerOfHanoiTask(language="ru", difficulty=2, detail_level=5)
        result = task.get_result()
        
        self.assertIn("диск", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_hanoi_en(self):
        """Тест Ханойской башни на английском."""
        task = TowerOfHanoiTask(language="en", difficulty=2, detail_level=5)
        result = task.get_result()
        
        self.assertIn("disk", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_hanoi_optimal_moves(self):
        """Проверка оптимального количества ходов."""
        # Для n дисков оптимальное решение = 2^n - 1
        for n in range(2, 6):
            task = TowerOfHanoiTask(num_disks=n)
            expected_moves = 2 ** n - 1
            self.assertEqual(len(task.moves), expected_moves, 
                           f"Для {n} дисков должно быть {expected_moves} ходов")
    
    def test_hanoi_moves_valid(self):
        """Проверка корректности ходов."""
        task = TowerOfHanoiTask(num_disks=3)
        
        # Симулируем выполнение ходов
        pegs = {'A': list(range(task.num_disks, 0, -1)), 'B': [], 'C': []}
        
        for disk, from_peg, to_peg in task.moves:
            # Проверяем, что диск на вершине исходного стержня
            self.assertTrue(len(pegs[from_peg]) > 0)
            self.assertEqual(pegs[from_peg][-1], disk)
            
            # Проверяем, что можно положить на целевой стержень
            if pegs[to_peg]:
                self.assertLess(disk, pegs[to_peg][-1])
            
            # Выполняем ход
            pegs[from_peg].pop()
            pegs[to_peg].append(disk)
        
        # Проверяем конечное состояние
        self.assertEqual(pegs['A'], [])
        self.assertEqual(pegs['B'], [])
        self.assertEqual(pegs['C'], list(range(task.num_disks, 0, -1)))
    
    def test_hanoi_difficulty_scaling(self):
        """Тест масштабирования сложности."""
        task_easy = TowerOfHanoiTask(difficulty=1)
        task_hard = TowerOfHanoiTask(difficulty=10)
        
        self.assertLess(task_easy.num_disks, task_hard.num_disks)
    
    def test_hanoi_get_task_type(self):
        """Тест типа задачи."""
        task = TowerOfHanoiTask()
        self.assertEqual(task.get_task_type(), "tower_of_hanoi")


if __name__ == '__main__':
    unittest.main()
