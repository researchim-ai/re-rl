# tests/test_arithmetic_task.py

import unittest
from re_rl.tasks.arithmetic_task import ArithmeticTask, ArithmeticConfig, DIFFICULTY_PRESETS


class TestArithmeticTask(unittest.TestCase):
    """Тесты для ArithmeticTask."""
    
    def test_basic_creation_ru(self):
        """Проверка создания базовой задачи на русском."""
        task = ArithmeticTask(difficulty=1, language="ru")
        result = task.get_result()
        
        self.assertIn("problem", result)
        self.assertIn("solution_steps", result)
        self.assertIn("final_answer", result)
        self.assertEqual(result["language"], "ru")
    
    def test_basic_creation_en(self):
        """Проверка создания базовой задачи на английском."""
        task = ArithmeticTask(difficulty=1, language="en")
        result = task.get_result()
        
        self.assertIn("problem", result)
        self.assertEqual(result["language"], "en")
    
    def test_difficulty_levels(self):
        """Проверка различных уровней сложности."""
        for difficulty in range(1, 11):
            task = ArithmeticTask(difficulty=difficulty, language="ru")
            result = task.get_result()
            self.assertIsNotNone(result["final_answer"])
    
    def test_from_difficulty_classmethod(self):
        """Проверка метода from_difficulty."""
        task = ArithmeticTask.from_difficulty(5, language="en", detail_level=2)
        result = task.get_result()
        
        self.assertIn("problem", result)
        self.assertEqual(task.difficulty, 5)
    
    def test_custom_config(self):
        """Проверка задачи с пользовательской конфигурацией."""
        config = ArithmeticConfig(
            num_operations=3,
            max_number=50,
            operations=['+', '-', '*'],
            use_parentheses=True
        )
        task = ArithmeticTask(config=config, language="ru")
        result = task.get_result()
        
        self.assertIn("problem", result)
        self.assertIsNotNone(result["final_answer"])
    
    def test_config_overrides(self):
        """Проверка переопределения параметров конфигурации."""
        task = ArithmeticTask(
            difficulty=3,
            language="ru",
            num_operations=5,  # Переопределяем пресет
            max_number=100
        )
        result = task.get_result()
        
        self.assertIsNotNone(result["final_answer"])
    
    def test_explicit_expression(self):
        """Проверка задачи с явно заданным выражением."""
        task = ArithmeticTask(
            expression="2 + 3 * 4",
            language="ru"
        )
        result = task.get_result()
        
        # 2 + 3 * 4 = 2 + 12 = 14
        self.assertEqual(float(result["final_answer"]), 14.0)
    
    def test_integer_result_guarantee(self):
        """Проверка гарантии целочисленного результата на низких уровнях."""
        for _ in range(10):
            task = ArithmeticTask(difficulty=1, language="ru")
            result = task.get_result()
            answer = float(result["final_answer"])
            self.assertEqual(answer, int(answer))
    
    def test_difficulty_presets_exist(self):
        """Проверка наличия всех пресетов сложности."""
        for i in range(1, 11):
            self.assertIn(i, DIFFICULTY_PRESETS)
            preset = DIFFICULTY_PRESETS[i]
            self.assertIsInstance(preset, ArithmeticConfig)
    
    def test_task_type(self):
        """Проверка типа задачи."""
        task = ArithmeticTask(difficulty=5, language="ru")
        self.assertEqual(task.get_task_type(), "arithmetic")


class TestDifficultyMixin(unittest.TestCase):
    """Тесты для системы сложности (DifficultyMixin)."""
    
    def test_linear_task_with_difficulty(self):
        """Проверка LinearTask с difficulty."""
        from re_rl.tasks.linear_task import LinearTask
        
        task = LinearTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result["final_answer"])
        self.assertEqual(task.difficulty, 3)
    
    def test_quadratic_task_with_difficulty(self):
        """Проверка QuadraticTask с difficulty."""
        from re_rl.tasks.quadratic_task import QuadraticTask
        
        task = QuadraticTask(difficulty=5, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result["final_answer"])
    
    def test_system_linear_with_difficulty(self):
        """Проверка SystemLinearTask с difficulty."""
        from re_rl.tasks.system_linear_task import SystemLinearTask
        
        task = SystemLinearTask(difficulty=4, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result["final_answer"])
    
    def test_graph_task_with_difficulty(self):
        """Проверка GraphTask с difficulty."""
        from re_rl.tasks.graph_task import GraphTask
        
        task = GraphTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result["final_answer"])
    
    def test_futoshiki_with_difficulty(self):
        """Проверка FutoshikiTask с difficulty."""
        from re_rl.tasks.futoshiki_task import FutoshikiTask
        
        task = FutoshikiTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result)
    
    def test_knights_knaves_with_difficulty(self):
        """Проверка KnightsKnavesTask с difficulty."""
        from re_rl.tasks.knights_knaves_task import KnightsKnavesTask
        
        task = KnightsKnavesTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result)
    
    def test_contradiction_with_difficulty(self):
        """Проверка ContradictionTask с difficulty."""
        from re_rl.tasks.contradiction_task import ContradictionTask
        
        task = ContradictionTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result)
    
    def test_difficulty_interpolation(self):
        """Проверка интерполяции параметров между пресетами."""
        from re_rl.tasks.linear_task import LinearTask
        
        # Интерполяция между пресетами
        task = LinearTask(difficulty=5, language="ru")
        self.assertIsNotNone(task.difficulty)


class TestDatasetGeneratorWithDifficulty(unittest.TestCase):
    """Тесты генератора датасетов с difficulty."""
    
    def test_generate_with_difficulty(self):
        """Проверка генерации задач с difficulty."""
        from re_rl.dataset_generator import DatasetGenerator
        
        generator = DatasetGenerator()
        dataset = generator.generate_dataset(
            task_types=["linear"],
            languages=["ru"],
            difficulties=[1, 5, 10],
            detail_levels=[2],
            tasks_per_type=1,
            use_difficulty=True
        )
        
        # 1 тип * 1 язык * 3 difficulty * 1 detail_level * 1 task = 3
        self.assertEqual(len(dataset), 3)
        
        # Проверяем, что каждая задача имеет difficulty
        for task in dataset:
            self.assertIn("difficulty", task)
    
    def test_generate_arithmetic_task(self):
        """Проверка генерации ArithmeticTask через DatasetGenerator."""
        from re_rl.dataset_generator import DatasetGenerator
        
        generator = DatasetGenerator()
        task = generator.generate_task("arithmetic", "ru", 3, difficulty=5)
        
        self.assertEqual(task["task_type"], "arithmetic")
        self.assertEqual(task["difficulty"], 5)


if __name__ == "__main__":
    unittest.main()
