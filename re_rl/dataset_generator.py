"""
Генератор датасетов для обучения LLM.

Поддерживает форматы:
- JSON (стандартный)
- JSONL (для потоковой обработки)
- SFT формат (instruction/input/output)

Форматы математических выражений:
- text: обычный текст (x² + 2x - 3)
- latex: LaTeX формат ($x^{2} + 2x - 3$)
"""

import json
import random
from typing import List, Dict, Any, Optional, Literal
from pathlib import Path
from datetime import datetime

try:
    from tqdm import tqdm
except ImportError:
    # Fallback если tqdm не установлен
    def tqdm(iterable, **kwargs):
        return iterable

# Тип формата вывода
OutputFormat = Literal["text", "latex"]

# Импорты из генераторов
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


class DatasetGenerator:
    """
    Генератор датасетов для обучения LLM математике и физике.
    
    Пример использования:
        generator = DatasetGenerator()
        
        # Быстрая генерация для SFT
        dataset = generator.generate_sft_dataset(
            task_types=["quadratic", "kinematics", "quantum"],
            num_samples=1000,
            language="ru"
        )
        generator.save_jsonl(dataset, "train.jsonl")
    """
    
    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Объединяем все генераторы
        self.math_generators = ALL_TASK_GENERATORS
        self.physics_generators = ALL_PHYSICS_TASK_GENERATORS
        self.all_generators = {**self.math_generators, **self.physics_generators}
    
    def list_available_tasks(self) -> Dict[str, List[str]]:
        """Возвращает список всех доступных типов задач."""
        return {
            "math": list(self.math_generators.keys()),
            "physics": list(self.physics_generators.keys()),
        }
    
    def generate_single_task(
        self,
        task_type: str,
        language: str = "ru",
        difficulty: int = 5,
        detail_level: int = 5,
        output_format: OutputFormat = "text"
    ) -> Dict[str, Any]:
        """
        Генерирует одну задачу.
        
        Args:
            task_type: Тип задачи (например, "quadratic", "kinematics")
            language: Язык ("ru" или "en")
            difficulty: Сложность 1-10
            detail_level: Детализация решения 1-10
            output_format: Формат вывода ("text" или "latex")
        
        Returns:
            Словарь с задачей и решением
        """
        if task_type not in self.all_generators:
            raise ValueError(f"Неизвестный тип: {task_type}. Доступные: {list(self.all_generators.keys())}")
        
        generator = self.all_generators[task_type]
        
        try:
            task = generator(
                language=language, 
                difficulty=difficulty, 
                detail_level=detail_level,
                output_format=output_format
            )
        except TypeError:
            # Не все задачи поддерживают output_format
            try:
                task = generator(language=language, difficulty=difficulty, detail_level=detail_level)
            except TypeError:
                # Некоторые старые задачи не поддерживают difficulty
                task = generator(language=language, detail_level=detail_level)
        
        # get_result() автоматически вызывает solve() если нужно
        result = task.get_result()
        
        return {
            "task_type": task_type,
            "language": language,
            "difficulty": difficulty,
            "output_format": output_format,
            "problem": result["problem"],
            "solution_steps": result.get("solution_steps", []),
            "final_answer": result["final_answer"],
            "prompt": result.get("prompt", ""),
        }
    
    def generate_sft_dataset(
        self,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        detail_level: int = 5,
        include_cot: bool = True,
        output_format: OutputFormat = "text",
        show_progress: bool = True,
    ) -> List[Dict[str, str]]:
        """
        Генерирует датасет в формате SFT (Supervised Fine-Tuning).
        
        Формат выхода:
        {
            "instruction": "Решите задачу пошагово.",
            "input": "Условие задачи...",
            "output": "Шаг 1: ...\nШаг 2: ...\n\nОтвет: ..."
        }
        
        Args:
            task_types: Список типов задач (None = все)
            num_samples: Общее количество примеров
            language: Язык ("ru" или "en")
            difficulties: Список сложностей для выборки (None = [1-10])
            detail_level: Детализация решения
            include_cot: Включать ли Chain-of-Thought (шаги решения)
            output_format: Формат математических выражений ("text" или "latex")
            show_progress: Показывать прогресс-бар (tqdm)
        
        Returns:
            Список примеров в SFT формате
        """
        if task_types is None:
            task_types = list(self.all_generators.keys())
        
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        # Инструкции на разных языках
        instructions = {
            "ru": "Решите задачу пошагово, объясняя каждый шаг рассуждения.",
            "en": "Solve the problem step by step, explaining each reasoning step.",
        }
        
        # Дополнение для LaTeX формата
        if output_format == "latex":
            instructions = {
                "ru": "Решите задачу пошагово, используя LaTeX для математических формул.",
                "en": "Solve the problem step by step, using LaTeX for mathematical formulas.",
            }
        
        dataset = []
        samples_per_type = max(1, num_samples // len(task_types))
        total_iterations = len(task_types) * samples_per_type
        
        # Создаём итератор с прогресс-баром
        task_iterator = []
        for task_type in task_types:
            for _ in range(samples_per_type):
                task_iterator.append(task_type)
        
        if show_progress:
            task_iterator = tqdm(
                task_iterator, 
                desc="Генерация задач", 
                unit="задач",
                total=total_iterations
            )
        
        for task_type in task_iterator:
            difficulty = random.choice(difficulties)
            
            try:
                task_data = self.generate_single_task(
                    task_type=task_type,
                    language=language,
                    difficulty=difficulty,
                    detail_level=detail_level,
                    output_format=output_format
                )
                
                # Формируем output
                final_ans = task_data['final_answer']
                
                # Проверяем, не начинается ли ответ уже с "Ответ:" / "Answer:"
                already_has_prefix = (
                    final_ans.startswith("Ответ:") or 
                    final_ans.startswith("Answer:") or
                    final_ans.startswith("Ответ ") or
                    final_ans.startswith("Answer ")
                )
                
                if include_cot and task_data["solution_steps"]:
                    steps_text = "\n".join(task_data["solution_steps"])
                    if already_has_prefix:
                        output = f"{steps_text}\n\n{final_ans}"
                    elif language == "ru":
                        output = f"{steps_text}\n\nОтвет: {final_ans}"
                    else:
                        output = f"{steps_text}\n\nAnswer: {final_ans}"
                else:
                    if already_has_prefix:
                        output = final_ans
                    elif language == "ru":
                        output = f"Ответ: {final_ans}"
                    else:
                        output = f"Answer: {final_ans}"
                
                # Очищаем input от служебных меток
                clean_input = task_data["problem"]
                # Убираем "type: structured_text_with_tags\n" и подобные строки
                if clean_input.startswith("type: "):
                    lines = clean_input.split('\n')
                    # Пропускаем первую строку с "type:"
                    clean_input = '\n'.join(lines[1:]).strip()
                
                dataset.append({
                    "instruction": instructions[language],
                    "input": clean_input,
                    "output": output,
                    "metadata": {
                        "task_type": task_type,
                        "difficulty": difficulty,
                        "language": language,
                        "output_format": output_format,
                    }
                })
                
            except Exception as e:
                # Пропускаем ошибочные задачи
                continue
        
        random.shuffle(dataset)
        return dataset[:num_samples]
    
    def generate_chat_dataset(
        self,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет в chat формате (messages).
        
        Формат:
        {
            "messages": [
                {"role": "user", "content": "Решите: ..."},
                {"role": "assistant", "content": "Шаг 1: ...\nОтвет: ..."}
            ]
        }
        """
        sft_data = self.generate_sft_dataset(
            task_types=task_types,
            num_samples=num_samples,
            language=language,
            difficulties=difficulties,
            show_progress=show_progress,
        )
        
        chat_data = []
        for item in sft_data:
            user_content = f"{item['instruction']}\n\n{item['input']}"
            chat_data.append({
                "messages": [
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": item["output"]}
                ],
                "metadata": item.get("metadata", {})
            })
        
        return chat_data
    
    def generate_dataset(
        self,
        task_types: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        difficulties: Optional[List[int]] = None,
        tasks_per_combination: int = 10,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет со всеми комбинациями параметров.
        
        Args:
            task_types: Типы задач
            languages: Языки ["ru", "en"]
            difficulties: Сложности [1-10]
            tasks_per_combination: Задач на комбинацию
            show_progress: Показывать прогресс-бар (tqdm)
        """
        if task_types is None:
            task_types = list(self.all_generators.keys())
        if languages is None:
            languages = ["ru", "en"]
        if difficulties is None:
            difficulties = [1, 3, 5, 7, 10]
        
        dataset = []
        
        # Подсчёт общего количества итераций
        total = len(task_types) * len(languages) * len(difficulties) * tasks_per_combination
        
        # Создаём итератор
        iterations = []
        for task_type in task_types:
            for language in languages:
                for difficulty in difficulties:
                    for _ in range(tasks_per_combination):
                        iterations.append((task_type, language, difficulty))
        
        if show_progress:
            iterations = tqdm(iterations, desc="Генерация задач", unit="задач", total=total)
        
        for task_type, language, difficulty in iterations:
            try:
                task_data = self.generate_single_task(
                    task_type=task_type,
                    language=language,
                    difficulty=difficulty,
                )
                dataset.append(task_data)
            except Exception:
                continue
        
        return dataset
    
    def save_json(self, dataset: List[Dict], filename: str):
        """Сохраняет датасет в JSON."""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(dataset)} примеров в {filepath}")
    
    def save_jsonl(self, dataset: List[Dict], filename: str):
        """Сохраняет датасет в JSONL (одна строка = один пример)."""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Сохранено {len(dataset)} примеров в {filepath}")
    
    def split_dataset(
        self,
        dataset: List[Dict],
        train_ratio: float = 0.9,
        seed: int = 42
    ) -> tuple:
        """Разделяет датасет на train/eval."""
        random.seed(seed)
        shuffled = dataset.copy()
        random.shuffle(shuffled)
        
        split_idx = int(len(shuffled) * train_ratio)
        return shuffled[:split_idx], shuffled[split_idx:]


def main():
    """Пример использования."""
    generator = DatasetGenerator()
    
    # Показать доступные задачи
    print("Доступные типы задач:")
    tasks = generator.list_available_tasks()
    print(f"  Математика ({len(tasks['math'])}): {tasks['math'][:5]}...")
    print(f"  Физика ({len(tasks['physics'])}): {tasks['physics']}")
    
    # Быстрая генерация SFT датасета
    print("\nГенерация SFT датасета...")
    dataset = generator.generate_sft_dataset(
        task_types=["quadratic", "kinematics", "quantum", "circuits"],
        num_samples=100,
        language="ru",
        difficulties=[3, 5, 7],
    )
    
    # Пример
    print(f"\nПример из датасета:")
    example = dataset[0]
    print(f"Instruction: {example['instruction']}")
    print(f"Input: {example['input'][:100]}...")
    print(f"Output: {example['output'][:200]}...")
    
    # Сохранение
    generator.save_jsonl(dataset, "sft_sample.jsonl")
    
    print(f"\nВсего сгенерировано: {len(dataset)} примеров")


if __name__ == "__main__":
    main()
