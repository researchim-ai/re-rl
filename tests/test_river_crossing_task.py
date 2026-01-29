# tests/test_river_crossing_task.py
import unittest
from re_rl.tasks.math.planning.river_crossing_task import RiverCrossingTask


class TestRiverCrossingTask(unittest.TestCase):
    """Тесты для RiverCrossingTask."""
    
    def test_classic_problem_ru(self):
        """Тест классической задачи (волк, коза, капуста) на русском."""
        task = RiverCrossingTask(language="ru", difficulty=1, detail_level=5)
        result = task.get_result()
        
        self.assertIn("волк", result["problem"].lower())
        self.assertIn("коз", result["problem"].lower())
        self.assertIn("капуст", result["problem"].lower())
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])
    
    def test_classic_problem_en(self):
        """Тест классической задачи на английском."""
        task = RiverCrossingTask(language="en", difficulty=1, detail_level=5)
        result = task.get_result()
        
        self.assertIn("wolf", result["problem"].lower())
        self.assertIn("goat", result["problem"].lower())
        self.assertIn("cabbage", result["problem"].lower())
    
    def test_classic_solution_valid(self):
        """Проверка корректности решения классической задачи."""
        task = RiverCrossingTask(problem_type="classic")
        
        # Решение должно существовать (известно, что 7 переправ)
        self.assertIsNotNone(task.solution_path)
        self.assertGreater(len(task.solution_path), 0)
        
        # Конечное состояние - все на правом берегу
        final_state = task.solution_path[-1][0]
        self.assertEqual(final_state, (1, 1, 1, 1))
    
    def test_missionaries_problem_ru(self):
        """Тест задачи миссионеров и каннибалов."""
        task = RiverCrossingTask(language="ru", difficulty=5, detail_level=5)
        result = task.get_result()
        
        self.assertEqual(task.problem_type, "missionaries")
        self.assertTrue(result["solution_steps"])
    
    def test_missionaries_solution_valid(self):
        """Проверка корректности решения задачи миссионеров."""
        task = RiverCrossingTask(problem_type="missionaries", missionaries=3, cannibals=3, capacity=2)
        
        if task.solution_path:
            # Конечное состояние - все на правом берегу
            final_state = task.solution_path[-1][0]
            self.assertEqual(final_state[0], 0)  # 0 миссионеров слева
            self.assertEqual(final_state[1], 0)  # 0 каннибалов слева
            self.assertEqual(final_state[2], 1)  # лодка справа
    
    def test_difficulty_presets(self):
        """Тест пресетов сложности."""
        task_easy = RiverCrossingTask(difficulty=1)
        self.assertEqual(task_easy.problem_type, "classic")
        
        task_medium = RiverCrossingTask(difficulty=5)
        self.assertEqual(task_medium.problem_type, "missionaries")
    
    def test_get_task_type(self):
        """Тест типа задачи."""
        task = RiverCrossingTask()
        self.assertEqual(task.get_task_type(), "river_crossing")


if __name__ == '__main__':
    unittest.main()
