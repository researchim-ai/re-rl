# tests/test_water_jug_task.py
import unittest
from math import gcd
from re_rl.tasks.math.planning.water_jug_task import WaterJugTask


class TestWaterJugTask(unittest.TestCase):
    """Тесты для WaterJugTask."""
    
    def test_water_jug_ru(self):
        """Тест задачи о кувшинах на русском."""
        task = WaterJugTask(language="ru", difficulty=1, detail_level=5)
        result = task.get_result()
        
        self.assertIn("кувшин", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_water_jug_en(self):
        """Тест задачи о кувшинах на английском."""
        task = WaterJugTask(language="en", difficulty=1, detail_level=5)
        result = task.get_result()
        
        self.assertIn("jug", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_water_jug_classic_3_5_4(self):
        """Тест классической задачи: 3л и 5л -> 4л."""
        task = WaterJugTask(capacities=(3, 5), target=4)
        
        self.assertTrue(task.is_solvable)
        self.assertIsNotNone(task.solution_path)
        self.assertGreater(len(task.solution_path), 0)
        
        # Проверяем, что в конце есть нужное количество воды
        final_state = task.solution_path[-1][0]
        self.assertIn(4, final_state)
    
    def test_water_jug_solvability(self):
        """Тест проверки разрешимости."""
        # Разрешимая: 3 и 5 -> 4 (НОД=1, 4 делится на 1)
        task_solvable = WaterJugTask(capacities=(3, 5), target=4)
        self.assertTrue(task_solvable.is_solvable)
        
        # Неразрешимая: 4 и 6 -> 5 (НОД=2, 5 не делится на 2)
        task_unsolvable = WaterJugTask(capacities=(4, 6), target=5)
        self.assertFalse(task_unsolvable.is_solvable)
    
    def test_water_jug_solution_valid(self):
        """Проверка корректности решения."""
        task = WaterJugTask(capacities=(3, 5), target=4)
        
        # Симулируем выполнение действий
        state = tuple(0 for _ in task.capacities)
        
        for i in range(1, len(task.solution_path)):
            new_state, action = task.solution_path[i]
            
            if action[0] == "fill":
                jug = action[1]
                expected = list(state)
                expected[jug] = task.capacities[jug]
                self.assertEqual(tuple(expected), new_state)
            elif action[0] == "empty":
                jug = action[1]
                expected = list(state)
                expected[jug] = 0
                self.assertEqual(tuple(expected), new_state)
            elif action[0] == "pour":
                from_jug, to_jug = action[1], action[2]
                amount = min(state[from_jug], task.capacities[to_jug] - state[to_jug])
                expected = list(state)
                expected[from_jug] -= amount
                expected[to_jug] += amount
                self.assertEqual(tuple(expected), new_state)
            
            state = new_state
    
    def test_water_jug_three_jugs(self):
        """Тест с тремя кувшинами."""
        task = WaterJugTask(capacities=(3, 5, 8), target=4)
        
        self.assertTrue(task.is_solvable)
        self.assertEqual(task.num_jugs, 3)
    
    def test_water_jug_difficulty_scaling(self):
        """Тест масштабирования сложности."""
        task_easy = WaterJugTask(difficulty=1)
        task_hard = WaterJugTask(difficulty=10)
        
        # Сложная задача имеет больше кувшинов или большие объёмы
        self.assertLessEqual(len(task_easy.capacities), len(task_hard.capacities))
    
    def test_water_jug_get_task_type(self):
        """Тест типа задачи."""
        task = WaterJugTask()
        self.assertEqual(task.get_task_type(), "water_jug")


if __name__ == '__main__':
    unittest.main()
