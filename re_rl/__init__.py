# re_rl/__init__.py

"""
RE-RL: Библиотека для генерации датасетов для обучения LLM математике и физике.

Основные компоненты:
- DatasetGenerator: Генерация single-turn и multi-turn датасетов
- MultiturnGenerator: Специализированный генератор multi-turn диалогов
- Tasks: 80+ типов математических и физических задач

Пример использования:
    from re_rl import DatasetGenerator
    
    generator = DatasetGenerator()
    
    # Single-turn SFT датасет
    dataset = generator.generate_sft_dataset(
        task_types=["arithmetic", "quadratic"],
        num_samples=1000,
        language="ru",
        reasoning_mode=True,
    )
    
    # Multi-turn датасет
    multiturn = generator.generate_multiturn_dataset(
        modes=["chain", "followup", "correction"],
        num_samples=500,
        language="ru",
    )
    
    generator.save_jsonl(dataset, "train.jsonl")
"""

from re_rl.dataset_generator import DatasetGenerator
from re_rl.multiturn_generator import MultiturnGenerator, MultiturnDialogue

__all__ = [
    "DatasetGenerator",
    "MultiturnGenerator",
    "MultiturnDialogue",
]

__version__ = "0.2.0"
