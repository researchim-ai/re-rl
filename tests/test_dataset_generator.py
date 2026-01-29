import unittest
from pathlib import Path
import json
import shutil
from re_rl.dataset_generator import DatasetGenerator


class TestDatasetGenerator(unittest.TestCase):
    def setUp(self):
        self.test_output_dir = Path("test_datasets")
        self.test_output_dir.mkdir(exist_ok=True)
        self.generator = DatasetGenerator(output_dir=str(self.test_output_dir))

    def tearDown(self):
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def test_list_available_tasks(self):
        """Проверка списка доступных задач"""
        tasks = self.generator.list_available_tasks()
        self.assertIn("math", tasks)
        self.assertIn("physics", tasks)
        self.assertIn("quadratic", tasks["math"])
        self.assertIn("kinematics", tasks["physics"])

    def test_generate_single_linear_task(self):
        """Проверка генерации линейной задачи"""
        task = self.generator.generate_single_task("linear", "ru", difficulty=5, detail_level=3)
        
        self.assertIn("problem", task)
        self.assertIn("solution_steps", task)
        self.assertIn("final_answer", task)
        self.assertIn("task_type", task)
        self.assertEqual(task["language"], "ru")

    def test_generate_single_quadratic_task(self):
        """Проверка генерации квадратной задачи"""
        task = self.generator.generate_single_task("quadratic", "en", difficulty=5, detail_level=2)
        
        self.assertIn("problem", task)
        self.assertIn("solution_steps", task)
        self.assertIn("final_answer", task)
        self.assertEqual(task["language"], "en")

    def test_generate_single_physics_task(self):
        """Проверка генерации физической задачи"""
        task = self.generator.generate_single_task("kinematics", "ru", difficulty=5)
        
        self.assertIn("problem", task)
        self.assertIn("solution_steps", task)
        self.assertIn("final_answer", task)

    def test_generate_sft_dataset(self):
        """Проверка генерации SFT датасета"""
        dataset = self.generator.generate_sft_dataset(
            task_types=["linear", "quadratic"],
            num_samples=4,
            language="ru"
        )
        
        self.assertEqual(len(dataset), 4)
        for sample in dataset:
            self.assertIn("instruction", sample)
            self.assertIn("input", sample)
            self.assertIn("output", sample)

    def test_generate_chat_dataset(self):
        """Проверка генерации chat датасета"""
        dataset = self.generator.generate_chat_dataset(
            task_types=["linear"],
            num_samples=2,
            language="ru"
        )
        
        self.assertEqual(len(dataset), 2)
        for sample in dataset:
            self.assertIn("messages", sample)
            self.assertTrue(len(sample["messages"]) >= 2)

    def test_generate_dataset_json(self):
        """Проверка генерации датасета в JSON"""
        dataset = self.generator.generate_dataset(
            task_types=["linear"],
            languages=["ru"],
            difficulties=[5],
            tasks_per_combination=2
        )
        
        self.assertGreater(len(dataset), 0)

    def test_save_jsonl(self):
        """Проверка сохранения в JSONL"""
        dataset = self.generator.generate_sft_dataset(
            task_types=["linear"],
            num_samples=2,
            language="ru"
        )
        
        output_path = "test.jsonl"
        self.generator.save_jsonl(dataset, output_path)
        
        # Файл сохраняется в output_dir генератора
        full_path = self.test_output_dir / output_path
        self.assertTrue(full_path.exists())
        
        # Проверяем содержимое
        with open(full_path, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)

    def test_latex_format(self):
        """Проверка LaTeX формата"""
        task = self.generator.generate_single_task(
            "quadratic", 
            "ru", 
            difficulty=5,
            output_format="latex"
        )
        
        # LaTeX должен содержать $ символы
        self.assertIn("$", task["problem"])

    def test_invalid_task_type(self):
        """Проверка обработки неверного типа задачи"""
        with self.assertRaises(ValueError):
            self.generator.generate_single_task("nonexistent_task", "ru")


if __name__ == "__main__":
    unittest.main()
