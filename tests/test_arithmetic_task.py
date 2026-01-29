# tests/test_arithmetic_task.py

import unittest
from re_rl.tasks.math.applied.arithmetic_task import ArithmeticTask, ArithmeticConfig


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
        """Проверка работы разных уровней сложности."""
        for diff in [1, 3, 5, 7, 10]:
            task = ArithmeticTask(difficulty=diff, language="ru")
            result = task.get_result()
            self.assertIn("final_answer", result)
    
    def test_custom_config(self):
        """Проверка с пользовательской конфигурацией."""
        config = ArithmeticConfig(
            num_operations=2,
            max_number=10,
            min_number=1,
            operations=["+", "-"],
            use_parentheses=False,
            use_fractions=False,
            use_percentages=False,
            use_powers=False,
            use_roots=False,
            max_nesting_depth=0,
            ensure_integer_result=True
        )
        task = ArithmeticTask(config=config, language="ru")
        result = task.get_result()
        
        self.assertIn("final_answer", result)
    
    def test_task_type(self):
        """Проверка типа задачи."""
        task = ArithmeticTask(difficulty=1, language="ru")
        self.assertEqual(task.get_task_type(), "arithmetic")


class TestDifficultyMixin(unittest.TestCase):
    """Тесты системы сложности."""
    
    def test_knights_knaves_with_difficulty(self):
        """Проверка KnightsKnavesTask с difficulty."""
        from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask
        
        task = KnightsKnavesTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result)
    
    def test_contradiction_with_difficulty(self):
        """Проверка ContradictionTask с difficulty."""
        from re_rl.tasks.math.logic.contradiction_task import ContradictionTask
        
        task = ContradictionTask(difficulty=3, language="ru")
        result = task.get_result()
        
        self.assertIsNotNone(result)
    
    def test_difficulty_interpolation(self):
        """Проверка интерполяции параметров между пресетами."""
        from re_rl.tasks.math.algebra.linear_task import LinearTask
        
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
            tasks_per_combination=1
        )
        
        # Проверяем что датасет не пустой
        self.assertGreater(len(dataset), 0)
    
    def test_generate_sft_arithmetic(self):
        """Проверка генерации SFT датасета с арифметикой."""
        from re_rl.dataset_generator import DatasetGenerator
        
        generator = DatasetGenerator()
        dataset = generator.generate_sft_dataset(
            task_types=["arithmetic"],
            num_samples=2,
            language="ru"
        )
        
        self.assertEqual(len(dataset), 2)


if __name__ == "__main__":
    unittest.main()
