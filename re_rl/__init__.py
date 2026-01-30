# re_rl/__init__.py

"""
RE-RL: Библиотека для генерации датасетов для обучения LLM математике и физике.

Основные компоненты:
- DatasetGenerator: Генерация single-turn и multi-turn датасетов
- MultiturnGenerator: Специализированный генератор multi-turn диалогов
- Tasks: 80+ типов математических и физических задач
- Аугментация: Вариативные формулировки задач для разнообразия данных

Пример использования:
    from re_rl import DatasetGenerator
    
    generator = DatasetGenerator()
    
    # Single-turn SFT датасет с аугментацией
    dataset = generator.generate_sft_dataset(
        task_types=["arithmetic", "quadratic"],
        num_samples=1000,
        language="ru",
        reasoning_mode=True,
        augment=True,  # Случайные формулировки задач
    )
    
    # Multi-turn датасет
    multiturn = generator.generate_multiturn_dataset(
        modes=["chain", "followup", "correction"],
        num_samples=500,
        language="ru",
    )
    
    generator.save_jsonl(dataset, "train.jsonl")

Аугментация формулировок:
    from re_rl import get_template, get_random_system_prompt, PROMPT_TEMPLATES
    
    # Получить случайный вариант формулировки
    templates = PROMPT_TEMPLATES["arithmetic"]
    problem = get_template(templates, "problem", "ru", augment=True, expression="2+3")
    # Результат может быть: "Вычислите: 2+3" или "Найдите: 2+3" или "Чему равно 2+3?"
    
    # Случайный системный промпт
    system = get_random_system_prompt("ru", style="teacher")
"""

from re_rl.dataset_generator import DatasetGenerator
from re_rl.multiturn_generator import MultiturnGenerator, MultiturnDialogue
from re_rl.tasks.prompts import (
    get_template,
    get_random_system_prompt,
    PROMPT_TEMPLATES,
    SYSTEM_PROMPT_VARIATIONS,
)

__all__ = [
    "DatasetGenerator",
    "MultiturnGenerator",
    "MultiturnDialogue",
    # Утилиты аугментации
    "get_template",
    "get_random_system_prompt",
    "PROMPT_TEMPLATES",
    "SYSTEM_PROMPT_VARIATIONS",
]

__version__ = "0.2.0"
