"""
Генератор датасетов для обучения LLM.

Поддерживает форматы:
- JSON (стандартный)
- JSONL (для потоковой обработки)
- SFT формат (instruction/input/output)
- Multi-turn chat формат (messages)

Форматы математических выражений:
- text: обычный текст (x² + 2x - 3)
- latex: LaTeX формат ($x^{2} + 2x - 3$)

Multi-turn режимы:
- chain: Последовательные задачи
- followup: Уточняющие вопросы
- variations: Вариации параметров
- correction: Исправление ошибок (для RLHF)
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
from re_rl.tasks.prompts import PROMPT_TEMPLATES

# Тип multi-turn режима
MultiturnMode = Literal["chain", "followup", "variations", "correction", "mixed"]


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

    @staticmethod
    def _clean_problem_text(problem: str) -> str:
        """Удаляет служебные префиксы из текста условия."""
        clean_input = problem or ""
        if clean_input.startswith("type: "):
            lines = clean_input.split("\n")
            clean_input = "\n".join(lines[1:]).strip()
        return clean_input

    @staticmethod
    def _build_sft_output(
        task_data: Dict[str, Any],
        language: str,
        include_cot: bool,
        reasoning_mode: bool,
    ) -> str:
        """Формирует целевой output для SFT/GRPO reference."""
        final_ans = task_data["final_answer"]
        if reasoning_mode:
            if include_cot and task_data.get("solution_steps"):
                steps_text = "\n".join(task_data["solution_steps"])
                return f"<think>\n{steps_text}\n</think>\n<answer>{final_ans}</answer>"
            return f"<think>\n\n</think>\n<answer>{final_ans}</answer>"

        already_has_prefix = (
            str(final_ans).startswith("Ответ:")
            or str(final_ans).startswith("Answer:")
            or str(final_ans).startswith("Ответ ")
            or str(final_ans).startswith("Answer ")
        )
        if include_cot and task_data.get("solution_steps"):
            steps_text = "\n".join(task_data["solution_steps"])
            if already_has_prefix:
                return f"{steps_text}\n\n{final_ans}"
            return f"{steps_text}\n\n{'Ответ:' if language == 'ru' else 'Answer:'} {final_ans}"
        if already_has_prefix:
            return str(final_ans)
        return f"{'Ответ:' if language == 'ru' else 'Answer:'} {final_ans}"
    
    def generate_single_task(
        self,
        task_type: str,
        language: str = "ru",
        difficulty: int = 5,
        detail_level: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True
    ) -> Dict[str, Any]:
        """
        Генерирует одну задачу.
        
        Args:
            task_type: Тип задачи (например, "quadratic", "kinematics")
            language: Язык ("ru" или "en")
            difficulty: Сложность 1-10
            detail_level: Детализация решения 1-10
            output_format: Формат вывода ("text" или "latex")
            reasoning_mode: Если True — выводит <think>/<answer> теги
            augment: Если True — использует случайные варианты формулировок
        
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
                output_format=output_format,
                reasoning_mode=reasoning_mode,
                augment=augment
            )
        except TypeError:
            # Не все задачи поддерживают все параметры
            try:
                task = generator(
                    language=language, 
                    difficulty=difficulty, 
                    detail_level=detail_level,
                    output_format=output_format,
                    augment=augment
                )
            except TypeError:
                try:
                    task = generator(
                        language=language, 
                        difficulty=difficulty, 
                        detail_level=detail_level,
                        augment=augment
                    )
                except TypeError:
                    try:
                        task = generator(language=language, difficulty=difficulty, detail_level=detail_level)
                    except TypeError:
                        # Некоторые старые задачи не поддерживают difficulty
                        task = generator(language=language, detail_level=detail_level)
            
            # Установим reasoning_mode вручную, если задача его поддерживает
            if hasattr(task, 'reasoning_mode'):
                task.reasoning_mode = reasoning_mode
        
        # get_result() автоматически вызывает solve() если нужно
        result = task.get_result()
        
        return {
            "task_type": task_type,
            "language": language,
            "difficulty": difficulty,
            "output_format": output_format,
            "reasoning_mode": reasoning_mode,
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
        reasoning_mode: bool = False,
        augment: bool = True,
        show_progress: bool = True,
    ) -> List[Dict[str, str]]:
        """
        Генерирует датасет в формате SFT (Supervised Fine-Tuning).
        
        Формат выхода (reasoning_mode=False):
        {
            "instruction": "Решите задачу пошагово.",
            "input": "Условие задачи...",
            "output": "Формула: ...\nПодстановка: ...\n\nОтвет: ..."
        }
        
        Формат выхода (reasoning_mode=True):
        {
            "instruction": "Решите задачу.",
            "input": "Условие задачи...",
            "output": "<think>\nДано: ...\nФормула: ...\n</think>\n<answer>...</answer>"
        }
        
        Args:
            task_types: Список типов задач (None = все)
            num_samples: Общее количество примеров
            language: Язык ("ru" или "en")
            difficulties: Список сложностей для выборки (None = [1-10])
            detail_level: Детализация решения
            include_cot: Включать ли Chain-of-Thought (шаги решения)
            output_format: Формат математических выражений ("text" или "latex")
            reasoning_mode: Если True — выводит <think>/<answer> теги
            augment: Если True — использует случайные варианты формулировок задач
            show_progress: Показывать прогресс-бар (tqdm)
        
        Returns:
            Список примеров в SFT формате
        """
        if task_types is None:
            task_types = list(self.all_generators.keys())
        
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        # Инструкции на разных языках
        if reasoning_mode:
            instructions = {
                "ru": "Решите задачу. Запишите рассуждения в <think></think>, ответ в <answer></answer>.",
                "en": "Solve the problem. Write reasoning in <think></think>, answer in <answer></answer>.",
            }
        else:
            instructions = {
                "ru": "Решите задачу пошагово, объясняя каждый шаг рассуждения.",
                "en": "Solve the problem step by step, explaining each reasoning step.",
            }
        
        # Дополнение для LaTeX формата
        if output_format == "latex" and not reasoning_mode:
            instructions = {
                "ru": "Решите задачу пошагово, используя LaTeX для математических формул.",
                "en": "Solve the problem step by step, using LaTeX for mathematical formulas.",
            }
        
        dataset = []
        max_attempts = max(num_samples * 20, len(task_types) * 10)
        attempts = range(max_attempts)
        if show_progress:
            attempts = tqdm(
                attempts,
                desc="Генерация задач",
                unit="попыток",
                total=max_attempts,
            )

        for _ in attempts:
            if len(dataset) >= num_samples:
                break

            task_type = random.choice(task_types)
            difficulty = random.choice(difficulties)

            try:
                task_data = self.generate_single_task(
                    task_type=task_type,
                    language=language,
                    difficulty=difficulty,
                    detail_level=detail_level,
                    output_format=output_format,
                    reasoning_mode=reasoning_mode,
                    augment=augment,
                )
            except Exception:
                continue

            clean_input = self._clean_problem_text(task_data["problem"])
            output = self._build_sft_output(
                task_data=task_data,
                language=language,
                include_cot=include_cot,
                reasoning_mode=reasoning_mode,
            )
            dataset.append(
                {
                    "instruction": instructions[language],
                    "input": clean_input,
                    "output": output,
                    "metadata": {
                        "task_type": task_type,
                        "difficulty": difficulty,
                        "language": language,
                        "output_format": output_format,
                        "reasoning_mode": reasoning_mode,
                    },
                }
            )

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
            chat_data.append({
                "messages": [
                    {"role": "system", "content": item["instruction"]},
                    {"role": "user", "content": item["input"]},
                    {"role": "assistant", "content": item["output"]}
                ],
                "metadata": item.get("metadata", {})
            })
        
        return chat_data

    def generate_pretrain_dataset(
        self,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        detail_level: int = 5,
        include_cot: bool = True,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        include_chat_tags: bool = True,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует pretrain-датасет в формате {"text": "..."}.
        """
        sft_data = self.generate_sft_dataset(
            task_types=task_types,
            num_samples=num_samples,
            language=language,
            difficulties=difficulties,
            detail_level=detail_level,
            include_cot=include_cot,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
            show_progress=show_progress,
        )

        rows = []
        for item in sft_data:
            if include_chat_tags:
                text = (
                    "<|system|>\n"
                    f"{item['instruction']}\n"
                    "<|user|>\n"
                    f"{item['input']}\n"
                    "<|assistant|>\n"
                    f"{item['output']}"
                )
            else:
                text = f"{item['instruction']}\n\n{item['input']}\n\n{item['output']}"
            rows.append({"text": text, "metadata": item.get("metadata", {})})
        return rows

    def generate_grpo_dataset(
        self,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        detail_level: int = 5,
        include_cot_in_reference: bool = False,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = True,
        augment: bool = True,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует GRPO-датасет в формате {"question": ..., "answer": ...}.
        """
        if task_types is None:
            task_types = list(self.all_generators.keys())
        if difficulties is None:
            difficulties = list(range(1, 11))

        dataset: List[Dict[str, Any]] = []
        max_attempts = max(num_samples * 20, len(task_types) * 10)
        attempts = range(max_attempts)
        if show_progress:
            attempts = tqdm(attempts, desc="Генерация GRPO", unit="попыток", total=max_attempts)

        for _ in attempts:
            if len(dataset) >= num_samples:
                break

            task_type = random.choice(task_types)
            difficulty = random.choice(difficulties)
            try:
                task_data = self.generate_single_task(
                    task_type=task_type,
                    language=language,
                    difficulty=difficulty,
                    detail_level=detail_level,
                    output_format=output_format,
                    reasoning_mode=reasoning_mode,
                    augment=augment,
                )
            except Exception:
                continue

            question = self._clean_problem_text(task_data["problem"])
            answer = self._build_sft_output(
                task_data=task_data,
                language=language,
                include_cot=include_cot_in_reference,
                reasoning_mode=reasoning_mode,
            )

            dataset.append(
                {
                    "question": question,
                    "answer": answer,
                    "task_type": task_type,
                    "difficulty": difficulty,
                    "language": language,
                    "metadata": {
                        "task_type": task_type,
                        "difficulty": difficulty,
                        "language": language,
                        "output_format": output_format,
                        "reasoning_mode": reasoning_mode,
                        "ref_final_answer": str(task_data["final_answer"]),
                    },
                }
            )

        return dataset
    
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
    
    # =========================================================================
    # Multi-turn генерация
    # =========================================================================
    
    def generate_multiturn_dataset(
        self,
        modes: Optional[List[MultiturnMode]] = None,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
        turns: int = 3,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует multi-turn датасет для обучения диалоговым навыкам.
        
        Args:
            modes: Типы диалогов. Доступные:
                - "chain": Последовательные задачи (результат предыдущей в следующей)
                - "followup": Уточняющие вопросы (почему, как ещё можно)
                - "variations": Вариации задачи (что если изменить параметр)
                - "correction": Исправление ошибок (для RLHF)
                - None = все типы
            task_types: Типы задач (None = подходящие для каждого mode)
            num_samples: Общее количество диалогов
            language: Язык ("ru" или "en")
            difficulties: Уровни сложности 1-10 (None = все)
            reasoning_mode: Использовать <think>/<answer> теги
            turns: Количество turns в диалоге
            show_progress: Показывать прогресс-бар
        
        Returns:
            Список диалогов в формате:
            {
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    ...
                ],
                "metadata": {"mode": "chain", "task_type": "arithmetic", ...}
            }
        
        Пример использования:
            generator = DatasetGenerator()
            
            # Смешанный multi-turn датасет
            dataset = generator.generate_multiturn_dataset(
                modes=["chain", "followup"],
                num_samples=1000,
                language="ru",
                reasoning_mode=True,
            )
            
            # Только correction для RLHF
            rlhf_data = generator.generate_multiturn_dataset(
                modes=["correction"],
                task_types=["arithmetic", "quadratic"],
                num_samples=500,
            )
            
            generator.save_jsonl(dataset, "multiturn_train.jsonl")
        """
        from re_rl.multiturn_generator import MultiturnGenerator
        
        mt_generator = MultiturnGenerator()
        return mt_generator.generate_multiturn_dataset(
            modes=modes,
            task_types=task_types,
            num_samples=num_samples,
            language=language,
            difficulties=difficulties,
            reasoning_mode=reasoning_mode,
            turns=turns,
            show_progress=show_progress,
        )
    
    def generate_chain_dataset(
        self,
        task_type: str = "arithmetic",
        num_samples: int = 100,
        turns: int = 3,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет chain-диалогов (последовательные задачи).
        
        Каждый диалог — цепочка связанных задач, где результат 
        предыдущей используется в следующей.
        
        Args:
            task_type: Тип задач ("arithmetic", "linear", "quadratic", "kinematics", "dynamics")
            num_samples: Количество диалогов
            turns: Количество задач в цепочке
            language: Язык
            difficulties: Уровни сложности
            reasoning_mode: Использовать <think>/<answer>
        """
        from re_rl.multiturn_generator import MultiturnGenerator
        
        mt_generator = MultiturnGenerator()
        return mt_generator.generate_chain_dialogues(
            task_type=task_type,
            num_dialogues=num_samples,
            turns=turns,
            language=language,
            difficulties=difficulties,
            reasoning_mode=reasoning_mode,
        )
    
    def generate_followup_dataset(
        self,
        task_type: str = "quadratic",
        num_samples: int = 100,
        num_followups: int = 2,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет с уточняющими вопросами.
        
        После решения задачи следуют вопросы:
        - "Почему ты использовал этот метод?"
        - "Можно ли решить по-другому?"
        - "Как проверить ответ?"
        
        Args:
            task_type: Тип задач
            num_samples: Количество диалогов
            num_followups: Количество уточняющих вопросов
            language: Язык
            difficulties: Уровни сложности
            reasoning_mode: Использовать <think>/<answer>
        """
        from re_rl.multiturn_generator import MultiturnGenerator
        
        mt_generator = MultiturnGenerator()
        return mt_generator.generate_followup_dialogues(
            task_type=task_type,
            num_dialogues=num_samples,
            num_followups=num_followups,
            language=language,
            difficulties=difficulties,
            reasoning_mode=reasoning_mode,
        )
    
    def generate_variation_dataset(
        self,
        task_type: str = "arithmetic",
        num_samples: int = 100,
        num_variations: int = 2,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет с вариациями задач.
        
        После решения задачи следуют вопросы:
        - "А если удвоить параметр?"
        - "А если значение будет отрицательным?"
        - "Обобщи решение для произвольного X"
        
        Args:
            task_type: Тип задач
            num_samples: Количество диалогов
            num_variations: Количество вариаций
            language: Язык
            difficulties: Уровни сложности
            reasoning_mode: Использовать <think>/<answer>
        """
        from re_rl.multiturn_generator import MultiturnGenerator
        
        mt_generator = MultiturnGenerator()
        return mt_generator.generate_variation_dialogues(
            task_type=task_type,
            num_dialogues=num_samples,
            num_variations=num_variations,
            language=language,
            difficulties=difficulties,
            reasoning_mode=reasoning_mode,
        )
    
    def generate_correction_dataset(
        self,
        task_type: str = "arithmetic",
        num_samples: int = 100,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует датасет для RLHF с исправлением ошибок.
        
        Диалог: задача → неправильный ответ → feedback → исправление.
        
        Полезно для обучения модели:
        - Признавать ошибки
        - Исправляться после feedback
        - Перепроверять решения
        
        Args:
            task_type: Тип задач
            num_samples: Количество диалогов
            language: Язык
            difficulties: Уровни сложности
            reasoning_mode: Использовать <think>/<answer>
        """
        from re_rl.multiturn_generator import MultiturnGenerator
        
        mt_generator = MultiturnGenerator()
        return mt_generator.generate_correction_dialogues(
            task_type=task_type,
            num_dialogues=num_samples,
            language=language,
            difficulties=difficulties,
            reasoning_mode=reasoning_mode,
        )


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
