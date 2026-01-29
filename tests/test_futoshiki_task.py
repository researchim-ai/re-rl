# tests/test_futoshiki_task.py
import unittest
from re_rl.tasks.math.logic.futoshiki_task import FutoshikiTask

class TestFutoshikiTask(unittest.TestCase):
    def test_futoshiki_ru(self):
        task = FutoshikiTask(language="ru", detail_level=5, size=4)
        result = task.get_result()
        
        self.assertIn("Задача Futoshiki", result["problem"])
        self.assertTrue(result["solution_steps"])  # должно быть несколько шагов
        self.assertTrue(result["final_answer"])    # либо "Нет решения", либо заполненная таблица

    def test_futoshiki_en(self):
        task = FutoshikiTask(language="en", detail_level=5, size=4)
        result = task.get_result()
        
        self.assertIn("Futoshiki puzzle", result["problem"])
        self.assertTrue(result["solution_steps"])
        self.assertTrue(result["final_answer"])

if __name__ == '__main__':
    unittest.main()
