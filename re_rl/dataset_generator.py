import json
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Импорты математических задач
from re_rl.tasks import (
    LinearTask,
    QuadraticTask,
    CubicTask,
    SystemLinearTask,
    ExponentialTask,
    LogarithmicTask,
    CalculusTask,
    GraphTask,
    AnalogicalTask,
    ContradictionTask,
    KnightsKnavesTask,
    FutoshikiTask,
    UrnProbabilityTask,
    TextStatsTask,
    ArithmeticTask,
    # Физические задачи
    KinematicsTask,
    DynamicsTask,
    EnergyTask,
    MomentumTask,
    CircuitsTask,
    ElectrostaticsTask,
    CapacitorsTask,
    GasLawsTask,
    HeatTransferTask,
    WavesTask,
    OpticsTask,
)

class DatasetGenerator:
    """
    Генератор датасетов для различных типов математических задач.
    """
    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Словарь доступных типов задач (математика)
        self.task_types = {
            "arithmetic": ArithmeticTask,
            "linear": LinearTask,
            "quadratic": QuadraticTask,
            "cubic": CubicTask,
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
            "text_stats": TextStatsTask,
            # Физические задачи
            "kinematics": KinematicsTask,
            "dynamics": DynamicsTask,
            "energy": EnergyTask,
            "momentum": MomentumTask,
            "circuits": CircuitsTask,
            "electrostatics": ElectrostaticsTask,
            "capacitors": CapacitorsTask,
            "gas_laws": GasLawsTask,
            "heat_transfer": HeatTransferTask,
            "waves": WavesTask,
            "optics": OpticsTask,
        }
        
        # Параметры генерации по умолчанию
        self.default_params = {
            "languages": ["ru", "en"],
            "detail_levels": [1, 2, 3, 4, 5],
            "difficulties": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "tasks_per_type": 100
        }

    def generate_task(
        self, 
        task_type: str, 
        language: str, 
        detail_level: int,
        difficulty: int = None
    ) -> Dict[str, Any]:
        """
        Генерирует одну задачу заданного типа.
        
        Args:
            task_type: Тип задачи
            language: Язык ("ru" или "en")
            detail_level: Уровень детализации решения
            difficulty: Уровень сложности (1-10). Если указан, параметры генерируются автоматически.
        """
        if task_type not in self.task_types:
            raise ValueError(f"Неизвестный тип задачи: {task_type}")
            
        task_class = self.task_types[task_type]
        
        # Если указан difficulty, создаём задачу через from_difficulty или с параметром difficulty
        if difficulty is not None:
            # Специальная обработка для задач с особыми требованиями
            if task_type == "analogical":
                descriptions = {
                    "ru": [
                        "Если река течёт, то вода движется. Аналогично, если электрический ток течёт, что происходит с электронами?",
                        "Дерево растёт из семени. По аналогии, из чего развивается бизнес?",
                        "Мозг обрабатывает информацию. Что аналогично делает компьютер?",
                        "Сердце качает кровь по телу. Какой механизм аналогично работает в системе отопления?",
                        "Корни питают дерево. Что аналогично питает компанию?"
                    ],
                    "en": [
                        "If a river flows, water moves. Similarly, if electric current flows, what happens to electrons?",
                        "A tree grows from a seed. By analogy, from what does a business develop?",
                        "The brain processes information. What does a computer analogously do?",
                        "The heart pumps blood through the body. What mechanism works similarly in a heating system?",
                        "Roots nourish the tree. What analogously nourishes a company?"
                    ]
                }
                description = random.choice(descriptions.get(language, descriptions["en"]))
                task = task_class(description=description, language=language, detail_level=detail_level)
            elif task_type in ("contradiction",):
                # Эти задачи НЕ принимают detail_level
                task = task_class(language=language, difficulty=difficulty)
            elif task_type in ("urn_probability",):
                # UrnProbabilityTask не поддерживает difficulty пока
                task = task_class(language=language)
            else:
                # Большинство задач поддерживают difficulty
                task = task_class(language=language, detail_level=detail_level, difficulty=difficulty)
            
            params = {"difficulty": difficulty}
        else:
            # Генерация через старые параметры
            try:
                params = self._generate_task_params(task_type)
            except NotImplementedError:
                raise NotImplementedError(f"Генерация параметров для {task_type} не реализована")
            
            # Специальная обработка для задач с особыми требованиями к параметрам
            if task_type == "analogical":
                descriptions = {
                    "ru": [
                        "Если река течёт, то вода движется. Аналогично, если электрический ток течёт, что происходит с электронами?",
                        "Дерево растёт из семени. По аналогии, из чего развивается бизнес?",
                        "Мозг обрабатывает информацию. Что аналогично делает компьютер?",
                        "Сердце качает кровь по телу. Какой механизм аналогично работает в системе отопления?",
                        "Корни питают дерево. Что аналогично питает компанию?"
                    ],
                    "en": [
                        "If a river flows, water moves. Similarly, if electric current flows, what happens to electrons?",
                        "A tree grows from a seed. By analogy, from what does a business develop?",
                        "The brain processes information. What does a computer analogously do?",
                        "The heart pumps blood through the body. What mechanism works similarly in a heating system?",
                        "Roots nourish the tree. What analogously nourishes a company?"
                    ]
                }
                params["description"] = random.choice(descriptions.get(language, descriptions["en"]))
                task = task_class(**params, language=language, detail_level=detail_level)
                
            elif task_type in ("contradiction", "urn_probability"):
                # Эти задачи НЕ принимают detail_level
                task = task_class(**params, language=language)
                
            else:
                # Стандартное создание задачи
                task = task_class(**params, language=language, detail_level=detail_level)
        
        result = task.get_result()
        
        return {
            "task_type": task_type,
            "language": language,
            "detail_level": detail_level,
            "difficulty": difficulty,
            "parameters": params,
            "result": result
        }

    def _generate_task_params(self, task_type: str) -> Dict[str, Any]:
        """
        Генерирует случайные параметры для конкретного типа задачи.
        Возвращает словарь параметров, соответствующих конструктору задачи.
        """
        if task_type not in self.task_types:
            raise NotImplementedError(f"Тип задачи {task_type} не реализован")
        
        if task_type == "arithmetic":
            # ArithmeticTask использует difficulty напрямую
            return {"difficulty": random.randint(1, 10)}
            
        elif task_type == "linear":
            # LinearTask(a, b, c, language, detail_level)
            a = random.randint(-10, 10)
            while a == 0:  # Избегаем деления на ноль
                a = random.randint(-10, 10)
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            return {"a": a, "b": b, "c": c}
            
        elif task_type == "quadratic":
            # QuadraticTask(a, b, c, language, detail_level)
            a = random.randint(-5, 5)
            while a == 0:
                a = random.randint(-5, 5)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            return {"a": a, "b": b, "c": c}
            
        elif task_type == "cubic":
            # CubicTask(a, b, c, d, language, detail_level)
            a = random.randint(-3, 3)
            while a == 0:
                a = random.randint(-3, 3)
            b = random.randint(-5, 5)
            c = random.randint(-5, 5)
            d = random.randint(-5, 5)
            return {"a": a, "b": b, "c": c, "d": d}
            
        elif task_type == "system_linear":
            # SystemLinearTask(matrix, language, detail_level)
            # matrix - расширенная матрица [A|b] размером n x (n+1)
            size = random.randint(2, 3)
            matrix = []
            for _ in range(size):
                row = [random.randint(-5, 5) for _ in range(size)]
                # Добавляем свободный член
                row.append(random.randint(-10, 10))
                matrix.append(row)
            return {"matrix": matrix}
            
        elif task_type == "exponential":
            # ExponentialTask(a, b, c, d, language, detail_level)
            return {
                "a": random.randint(1, 5),
                "b": random.randint(1, 3),
                "c": random.randint(-5, 5),
                "d": random.randint(1, 10)
            }
            
        elif task_type == "logarithmic":
            # LogarithmicTask(a, b, c, d, language, detail_level)
            return {
                "a": random.randint(1, 5),
                "b": random.randint(1, 3),
                "c": random.randint(-5, 5),
                "d": random.randint(1, 10)
            }
            
        elif task_type == "calculus":
            # CalculusTask(task_type, degree, function, language, detail_level)
            calc_types = ["differentiation", "integration"]
            return {
                "task_type": random.choice(calc_types),
                "degree": random.randint(1, 3),
                "function": None  # Будет сгенерирована автоматически
            }
            
        elif task_type == "graph":
            # GraphTask(task_type, num_nodes, edge_prob, language, detail_level)
            graph_types = ["shortest_path", "minimum_spanning_tree", "diameter", "clustering_coefficient"]
            return {
                "task_type": random.choice(graph_types),
                "num_nodes": random.randint(5, 10),
                "edge_prob": random.uniform(0.3, 0.6)
            }
            
        elif task_type == "analogical":
            # AnalogicalTask(description, language, detail_level)
            descriptions = {
                "ru": [
                    "Если река течёт, то вода движется. Аналогично, если электрический ток течёт, что происходит с электронами?",
                    "Дерево растёт из семени. По аналогии, из чего развивается бизнес?",
                    "Мозг обрабатывает информацию. Что аналогично делает компьютер?",
                    "Сердце качает кровь по телу. Какой механизм аналогично работает в системе отопления?",
                    "Корни питают дерево. Что аналогично питает компанию?"
                ],
                "en": [
                    "If a river flows, water moves. Similarly, if electric current flows, what happens to electrons?",
                    "A tree grows from a seed. By analogy, from what does a business develop?",
                    "The brain processes information. What does a computer analogously do?",
                    "The heart pumps blood through the body. What mechanism works similarly in a heating system?",
                    "Roots nourish the tree. What analogously nourishes a company?"
                ]
            }
            return {"description": None}  # Будет выбрано при создании с учётом языка
            
        elif task_type == "contradiction":
            # ContradictionTask(language, num_statements) - БЕЗ detail_level!
            return {"num_statements": random.randint(10, 25)}
            
        elif task_type == "knights_knaves":
            # KnightsKnavesTask(language, detail_level, complexity)
            return {"complexity": random.randint(1, 3)}
            
        elif task_type == "futoshiki":
            # FutoshikiTask(language, detail_level, size, num_inequalities)
            size = random.randint(4, 5)
            return {
                "size": size,
                "num_inequalities": random.randint(size, size * 2)
            }
            
        elif task_type == "urn_probability":
            # UrnProbabilityTask(language, count_containers, draws) - БЕЗ detail_level!
            return {
                "count_containers": random.randint(2, 4),
                "draws": random.randint(1, 3)
            }
            
        elif task_type == "text_stats":
            # TextStatsTask(language, detail_level, text, substring, allow_overlapping, text_gen_mode, mix_ratio)
            return {
                "text": None,  # Будет сгенерирован автоматически
                "substring": None,  # Будет выбрана автоматически
                "allow_overlapping": random.choice([True, False]),
                "text_gen_mode": random.choice(["words", "letters", "mixed"]),
                "mix_ratio": random.uniform(0.3, 0.7)
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
                        difficulties: Optional[List[int]] = None,
                        tasks_per_type: int = 100,
                        use_difficulty: bool = True) -> List[Dict[str, Any]]:
        """
        Генерирует полный датасет задач.
        
        Args:
            task_types: Список типов задач (по умолчанию все)
            languages: Список языков (по умолчанию ["ru", "en"])
            detail_levels: Уровни детализации решения (по умолчанию [1-5])
            difficulties: Уровни сложности (по умолчанию [1-10])
            tasks_per_type: Количество задач для каждой комбинации параметров
            use_difficulty: Использовать ли difficulty для генерации (True) или старый способ (False)
            
        Returns:
            Список сгенерированных задач
        """
        if task_types is None:
            task_types = list(self.task_types.keys())
        if languages is None:
            languages = self.default_params["languages"]
        if detail_levels is None:
            detail_levels = self.default_params["detail_levels"]
        if difficulties is None:
            difficulties = self.default_params.get("difficulties", [5])
            
        dataset = []
        
        if use_difficulty:
            # Новый способ: генерация по уровням сложности
            for task_type in task_types:
                for language in languages:
                    for difficulty in difficulties:
                        for detail_level in detail_levels:
                            for _ in range(tasks_per_type):
                                task = self.generate_task(
                                    task_type, language, detail_level, 
                                    difficulty=difficulty
                                )
                                dataset.append(task)
        else:
            # Старый способ: генерация через параметры
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