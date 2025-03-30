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
        shutil.rmtree(self.test_output_dir)

    def test_generate_linear_task(self):
        """Проверка генерации линейной задачи"""
        task = self.generator.generate_task("linear", "ru", 3)
        
        self.assertEqual(task["task_type"], "linear")
        self.assertEqual(task["language"], "ru")
        self.assertEqual(task["detail_level"], 3)
        self.assertIn("parameters", task)
        self.assertIn("result", task)
        
        # Проверка параметров
        params = task["parameters"]
        self.assertIn("a", params)
        self.assertIn("b", params)
        self.assertIn("c", params)
        
        # Проверка результата
        result = task["result"]
        self.assertIn("problem", result)
        self.assertIn("prompt", result)
        self.assertIn("solution_steps", result)
        self.assertIn("final_answer", result)

    def test_generate_quadratic_task(self):
        """Проверка генерации квадратной задачи"""
        task = self.generator.generate_task("quadratic", "en", 2)
        
        self.assertEqual(task["task_type"], "quadratic")
        self.assertEqual(task["language"], "en")
        self.assertEqual(task["detail_level"], 2)
        self.assertIn("parameters", task)
        self.assertIn("result", task)
        
        # Проверка параметров
        params = task["parameters"]
        self.assertIn("a", params)
        self.assertIn("b", params)
        self.assertIn("c", params)

    def test_generate_dataset(self):
        """Проверка генерации полного датасета"""
        dataset = self.generator.generate_dataset(
            task_types=["linear"],
            languages=["ru"],
            detail_levels=[1, 2],
            tasks_per_type=2
        )
        
        self.assertEqual(len(dataset), 4)  # 2 задачи * 2 уровня детализации
        
        # Проверка структуры каждой задачи
        for task in dataset:
            self.assertIn("task_type", task)
            self.assertIn("language", task)
            self.assertIn("detail_level", task)
            self.assertIn("parameters", task)
            self.assertIn("result", task)

    def test_save_dataset(self):
        """Проверка сохранения датасета"""
        dataset = self.generator.generate_dataset(
            task_types=["linear"],
            languages=["ru"],
            detail_levels=[1],
            tasks_per_type=1
        )
        
        filename = "test_dataset.json"
        self.generator.save_dataset(dataset, filename)
        
        # Проверка существования файла
        output_file = self.test_output_dir / filename
        self.assertTrue(output_file.exists())
        
        # Проверка содержимого файла
        with open(output_file, "r", encoding="utf-8") as f:
            loaded_dataset = json.load(f)
            self.assertEqual(len(loaded_dataset), 1)
            self.assertEqual(loaded_dataset[0]["task_type"], "linear")
            self.assertEqual(loaded_dataset[0]["language"], "ru")
            self.assertEqual(loaded_dataset[0]["detail_level"], 1)

    def test_invalid_task_type(self):
        """Проверка обработки неверного типа задачи"""
        with self.assertRaises(ValueError):
            self.generator.generate_task("invalid_type", "ru", 1)

    def test_invalid_parameters(self):
        """Проверка обработки нереализованных параметров"""
        with self.assertRaises(NotImplementedError):
            self.generator._generate_task_params("invalid_task_type")

    def test_generate_system_linear_params(self):
        """Проверка генерации параметров для системы линейных уравнений"""
        params = self.generator._generate_task_params("system_linear")
        
        self.assertIn("size", params)
        self.assertIn("coefficients", params)
        self.assertIn("constants", params)
        
        size = params["size"]
        self.assertTrue(2 <= size <= 3)
        self.assertEqual(len(params["coefficients"]), size)
        self.assertEqual(len(params["constants"]), size)

    def test_generate_exponential_params(self):
        """Проверка генерации параметров для экспоненциального уравнения"""
        params = self.generator._generate_task_params("exponential")
        
        self.assertIn("a", params)
        self.assertIn("b", params)
        self.assertIn("c", params)
        self.assertIn("d", params)
        
        self.assertTrue(1 <= params["a"] <= 5)
        self.assertTrue(1 <= params["b"] <= 3)
        self.assertTrue(-5 <= params["c"] <= 5)
        self.assertTrue(1 <= params["d"] <= 10)

    def test_generate_calculus_params(self):
        """Проверка генерации параметров для задач по анализу"""
        params = self.generator._generate_task_params("calculus")
        
        self.assertIn("task_type", params)
        self.assertIn("function", params)
        
        self.assertIn(params["task_type"], ["derivative", "integral"])
        self.assertIsInstance(params["function"], str)

    def test_generate_graph_params(self):
        """Проверка генерации параметров для задач на графах"""
        params = self.generator._generate_task_params("graph")
        
        self.assertIn("graph_type", params)
        self.assertIn("vertices", params)
        self.assertIn("edges", params)
        
        self.assertIn(params["graph_type"], ["shortest_path", "mst", "diameter", "clustering"])
        self.assertTrue(4 <= params["vertices"] <= 8)
        self.assertTrue(6 <= params["edges"] <= 12)

    def test_generate_analogical_params(self):
        """Проверка генерации параметров для задач на аналогии"""
        params = self.generator._generate_task_params("analogical")
        
        self.assertIn("source_domain", params)
        self.assertIn("target_domain", params)
        self.assertIn("complexity", params)
        
        self.assertIn(params["source_domain"], ["математика", "физика", "химия"])
        self.assertIn(params["target_domain"], ["биология", "экономика", "социология"])
        self.assertTrue(1 <= params["complexity"] <= 3)

    def test_generate_contradiction_params(self):
        """Проверка генерации параметров для задач на противоречия"""
        params = self.generator._generate_task_params("contradiction")
        
        self.assertIn("num_statements", params)
        self.assertIn("domain", params)
        
        self.assertTrue(4 <= params["num_statements"] <= 6)
        self.assertIn(params["domain"], ["наука", "история", "география", "биология"])

    def test_generate_knights_knaves_params(self):
        """Проверка генерации параметров для задач о рыцарях и лжецах"""
        params = self.generator._generate_task_params("knights_knaves")
        
        self.assertIn("num_persons", params)
        self.assertIn("complexity", params)
        
        self.assertTrue(2 <= params["num_persons"] <= 3)
        self.assertTrue(1 <= params["complexity"] <= 3)

    def test_generate_futoshiki_params(self):
        """Проверка генерации параметров для задач Futoshiki"""
        params = self.generator._generate_task_params("futoshiki")
        
        self.assertIn("size", params)
        self.assertIn("initial_grid", params)
        self.assertIn("inequalities", params)
        
        size = params["size"]
        self.assertTrue(3 <= size <= 4)
        self.assertEqual(len(params["initial_grid"]), size)
        self.assertEqual(len(params["initial_grid"][0]), size)

    def test_generate_urn_probability_params(self):
        """Проверка генерации параметров для задач с вероятностями"""
        params = self.generator._generate_task_params("urn_probability")
        
        self.assertIn("count_containers", params)
        self.assertIn("items_per_container", params)
        self.assertIn("colors", params)
        
        self.assertTrue(2 <= params["count_containers"] <= 3)
        self.assertTrue(3 <= params["items_per_container"] <= 5)
        self.assertEqual(len(params["colors"]), 3)

    def test_generate_text_stats_params(self):
        """Проверка генерации параметров для задач со статистикой текста"""
        params = self.generator._generate_task_params("text_stats")
        
        self.assertIn("text_length", params)
        self.assertIn("substring_length", params)
        self.assertIn("allow_overlapping", params)
        
        self.assertTrue(100 <= params["text_length"] <= 200)
        self.assertTrue(2 <= params["substring_length"] <= 4)
        self.assertIsInstance(params["allow_overlapping"], bool)

if __name__ == '__main__':
    unittest.main() 