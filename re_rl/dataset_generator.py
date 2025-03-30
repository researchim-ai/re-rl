import json
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.system_linear_task import SystemLinearTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.analogical_task import AnalogicalTask
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.futoshiki_task import FutoshikiTask
from re_rl.tasks.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.text_stats_task import TextStatsTask

class DatasetGenerator:
    """
    Генератор датасетов для различных типов математических задач.
    """
    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Словарь доступных типов задач
        self.task_types = {
            "linear": LinearTask,
            "quadratic": QuadraticTask,
            "system_linear": SystemLinearTask,
            "exponential": ExponentialTask,
            "logarithmic": LogarithmicTask,
            "calculus": CalculusTask,
            "graph": GraphTask,
            "analogical": AnalogicalTask,
            "contradiction": ContradictionTask,
            "knights_knaves": KnightsKnavesTask,
            "futoshiki": FutoshikiTask,
            "urn_probability": UrnProbabilityTask,
            "text_stats": TextStatsTask
        }
        
        # Параметры генерации по умолчанию
        self.default_params = {
            "languages": ["ru", "en"],
            "detail_levels": [1, 2, 3, 4, 5],
            "tasks_per_type": 100
        }

    def generate_task(self, task_type: str, language: str, detail_level: int) -> Dict[str, Any]:
        """
        Генерирует одну задачу заданного типа.
        """
        if task_type not in self.task_types:
            raise ValueError(f"Неизвестный тип задачи: {task_type}")
            
        task_class = self.task_types[task_type]
        
        # Генерация случайных параметров для задачи
        params = self._generate_task_params(task_type)
        
        # Создание и решение задачи
        task = task_class(**params, language=language, detail_level=detail_level)
        result = task.get_result()
        
        return {
            "task_type": task_type,
            "language": language,
            "detail_level": detail_level,
            "parameters": params,
            "result": result
        }

    def _generate_task_params(self, task_type: str) -> Dict[str, Any]:
        """
        Генерирует случайные параметры для конкретного типа задачи.
        """
        if task_type == "linear":
            # Генерируем параметры так, чтобы уравнение имело решение
            a = random.randint(-10, 10)
            while a == 0:  # Избегаем деления на ноль
                a = random.randint(-10, 10)
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            return {
                "a": a,
                "b": b,
                "c": c
            }
        elif task_type == "quadratic":
            # Генерируем параметры так, чтобы уравнение имело решение
            a = random.randint(-5, 5)
            while a == 0:  # Избегаем деления на ноль
                a = random.randint(-5, 5)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            return {
                "a": a,
                "b": b,
                "c": c
            }
        elif task_type == "system_linear":
            size = random.randint(2, 3)  # Системы 2x2 или 3x3
            return {
                "size": size,
                "coefficients": [[random.randint(-5, 5) for _ in range(size)] for _ in range(size)],
                "constants": [random.randint(-10, 10) for _ in range(size)]
            }
        elif task_type == "exponential":
            return {
                "a": random.randint(1, 5),
                "b": random.randint(1, 3),
                "c": random.randint(-5, 5),
                "d": random.randint(1, 10)
            }
        elif task_type == "logarithmic":
            return {
                "a": random.randint(1, 5),
                "b": random.randint(1, 3),
                "c": random.randint(-5, 5),
                "d": random.randint(1, 10)
            }
        elif task_type == "calculus":
            task_types = ["derivative", "integral"]
            functions = [
                "x^2", "x^3", "sin(x)", "cos(x)", "exp(x)",
                "log(x)", "x^2 + 2*x + 1", "x^3 - 3*x^2 + 3*x - 1"
            ]
            return {
                "task_type": random.choice(task_types),
                "function": random.choice(functions)
            }
        elif task_type == "graph":
            graph_types = ["shortest_path", "mst", "diameter", "clustering"]
            return {
                "graph_type": random.choice(graph_types),
                "vertices": random.randint(4, 8),
                "edges": random.randint(6, 12)
            }
        elif task_type == "analogical":
            return {
                "source_domain": random.choice(["математика", "физика", "химия"]),
                "target_domain": random.choice(["биология", "экономика", "социология"]),
                "complexity": random.randint(1, 3)
            }
        elif task_type == "contradiction":
            return {
                "num_statements": random.randint(4, 6),
                "domain": random.choice(["наука", "история", "география", "биология"])
            }
        elif task_type == "knights_knaves":
            return {
                "num_persons": random.randint(2, 3),
                "complexity": random.randint(1, 3)
            }
        elif task_type == "futoshiki":
            size = random.randint(3, 4)
            return {
                "size": size,
                "initial_grid": [[0 for _ in range(size)] for _ in range(size)],
                "inequalities": self._generate_futoshiki_inequalities(size)
            }
        elif task_type == "urn_probability":
            return {
                "count_containers": random.randint(2, 3),
                "items_per_container": random.randint(3, 5),
                "colors": random.sample(["красный", "синий", "зелёный", "белый", "чёрный"], 3)
            }
        elif task_type == "text_stats":
            return {
                "text_length": random.randint(100, 200),
                "substring_length": random.randint(2, 4),
                "allow_overlapping": random.choice([True, False])
            }
        else:
            raise NotImplementedError(f"Генерация параметров для {task_type} не реализована")

    def _generate_futoshiki_inequalities(self, size: int) -> List[Dict[str, int]]:
        """
        Генерирует случайные неравенства для задачи Futoshiki.
        """
        inequalities = []
        max_inequalities = size * (size - 1)
        num_inequalities = random.randint(max_inequalities // 2, max_inequalities)
        
        for _ in range(num_inequalities):
            r1, c1 = random.randint(0, size-1), random.randint(0, size-1)
            r2, c2 = random.randint(0, size-1), random.randint(0, size-1)
            
            # Проверяем, что ячейки соседние
            if (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2):
                inequalities.append({
                    "r1": r1, "c1": c1,
                    "r2": r2, "c2": c2,
                    "operator": "<" if random.random() < 0.5 else ">"
                })
        
        return inequalities

    def generate_dataset(self, 
                        task_types: Optional[List[str]] = None,
                        languages: Optional[List[str]] = None,
                        detail_levels: Optional[List[int]] = None,
                        tasks_per_type: int = 100) -> List[Dict[str, Any]]:
        """
        Генерирует полный датасет задач.
        """
        if task_types is None:
            task_types = list(self.task_types.keys())
        if languages is None:
            languages = self.default_params["languages"]
        if detail_levels is None:
            detail_levels = self.default_params["detail_levels"]
            
        dataset = []
        
        for task_type in task_types:
            for language in languages:
                for detail_level in detail_levels:
                    for _ in range(tasks_per_type):
                        task = self.generate_task(task_type, language, detail_level)
                        dataset.append(task)
                        
        return dataset

    def save_dataset(self, dataset: List[Dict[str, Any]], filename: Optional[str] = None):
        """
        Сохраняет датасет в JSON файл.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dataset_{timestamp}.json"
            
        output_file = self.output_dir / filename
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            
        print(f"Датасет сохранен в {output_file}")

def main():
    """
    Пример использования генератора датасетов.
    """
    generator = DatasetGenerator()
    
    # Генерация датасета с настройками по умолчанию
    dataset = generator.generate_dataset()
    
    # Сохранение датасета
    generator.save_dataset(dataset)
    
    print(f"Сгенерировано {len(dataset)} задач")

if __name__ == "__main__":
    main() 