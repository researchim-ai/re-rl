# re_rl/tasks/formal/dataset_generator.py
"""
Генератор датасетов для обучения моделей доказательства теорем.

Собирает пары (state, tactic) из:
1. BFS исследования графа состояний (как LeanNavigator)
2. Трассировки существующих репозиториев Lean

Экспортирует в форматы:
- JSON (для HuggingFace datasets)
- SFT формат (instruction/input/output)
- Chat формат (messages)
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Callable
from dataclasses import dataclass, field, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import random

from .state_explorer import (
    StateExplorer,
    ExplorationResult,
    TrainingPair,
    ExplorationStats,
)
from .tactic_generator import TacticGenerator

logger = logging.getLogger(__name__)


@dataclass
class DatasetConfig:
    """Конфигурация генерации датасета."""
    
    # Репозиторий
    repo_url: str = ""
    repo_commit: str = ""
    
    # Лимиты на теорему
    max_steps_per_theorem: int = 5000
    max_time_per_theorem: int = 120  # секунды
    max_depth: int = 15
    
    # Глобальные лимиты
    max_theorems: int = 1000
    max_total_pairs: int = 100000
    
    # Параллелизация
    num_workers: int = 1
    
    # Фильтры
    min_proof_length: int = 1
    max_proof_length: int = 20
    include_negative_examples: bool = True
    negative_ratio: float = 0.2  # % негативных примеров
    
    # Вывод
    output_dir: str = "./lean_dataset"
    output_format: str = "json"  # "json", "jsonl", "parquet"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DatasetStats:
    """Статистика сгенерированного датасета."""
    total_theorems_processed: int = 0
    total_theorems_proved: int = 0
    total_training_pairs: int = 0
    total_positive_pairs: int = 0
    total_negative_pairs: int = 0
    total_time_seconds: float = 0.0
    avg_pairs_per_theorem: float = 0.0
    avg_time_per_theorem: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LeanDatasetGenerator:
    """
    Генератор датасетов из Lean репозиториев.
    
    Использует LeanDojo для трассировки и StateExplorer для BFS.
    
    Example:
        >>> generator = LeanDatasetGenerator(config)
        >>> generator.generate_from_repo(
        ...     "https://github.com/leanprover-community/mathlib4",
        ...     "commit_hash"
        ... )
        >>> generator.save("./output")
    """
    
    def __init__(self, config: Optional[DatasetConfig] = None):
        self.config = config or DatasetConfig()
        self.training_pairs: List[TrainingPair] = []
        self.stats = DatasetStats()
        self._explorer = StateExplorer(
            max_steps=self.config.max_steps_per_theorem,
            max_time=self.config.max_time_per_theorem,
            max_depth=self.config.max_depth,
        )
    
    def generate_from_repo(
        self,
        repo_url: str,
        commit: str,
        file_paths: Optional[List[str]] = None,
        theorem_filter: Optional[Callable[[Any], bool]] = None,
    ) -> DatasetStats:
        """
        Генерирует датасет из Lean репозитория.
        
        Args:
            repo_url: URL Git репозитория
            commit: Коммит для трассировки
            file_paths: Список файлов (если None — все)
            theorem_filter: Функция фильтрации теорем
            
        Returns:
            Статистика генерации
        """
        try:
            from lean_dojo import LeanGitRepo, Theorem, trace
        except ImportError:
            raise ImportError(
                "LeanDojo is required. Install with: pip install lean-dojo"
            )
        
        start_time = time.time()
        
        # Трассируем репозиторий
        logger.info(f"Tracing repository: {repo_url}@{commit}")
        repo = LeanGitRepo(repo_url, commit)
        traced_repo = trace(repo)
        
        # Получаем теоремы
        theorems = list(traced_repo.get_traced_theorems())
        logger.info(f"Found {len(theorems)} theorems")
        
        # Фильтруем по файлам
        if file_paths:
            theorems = [t for t in theorems if t.file_path in file_paths]
        
        # Применяем кастомный фильтр
        if theorem_filter:
            theorems = [t for t in theorems if theorem_filter(t)]
        
        # Ограничиваем количество
        if len(theorems) > self.config.max_theorems:
            theorems = random.sample(theorems, self.config.max_theorems)
        
        logger.info(f"Processing {len(theorems)} theorems")
        
        # Обрабатываем теоремы
        for i, traced_thm in enumerate(theorems):
            if len(self.training_pairs) >= self.config.max_total_pairs:
                logger.info("Reached max_total_pairs limit")
                break
            
            try:
                theorem = Theorem(repo, traced_thm.file_path, traced_thm.full_name)
                result, pairs, stats = self._process_theorem(theorem)
                
                self.stats.total_theorems_processed += 1
                if result == ExplorationResult.SUCCESS:
                    self.stats.total_theorems_proved += 1
                
                self._add_pairs(pairs)
                
                if (i + 1) % 10 == 0:
                    logger.info(
                        f"Processed {i+1}/{len(theorems)} theorems, "
                        f"{len(self.training_pairs)} pairs collected"
                    )
                    
            except Exception as e:
                logger.warning(f"Error processing {traced_thm.full_name}: {e}")
                continue
        
        # Финальная статистика
        self.stats.total_time_seconds = time.time() - start_time
        self.stats.total_training_pairs = len(self.training_pairs)
        
        if self.stats.total_theorems_processed > 0:
            self.stats.avg_pairs_per_theorem = (
                self.stats.total_training_pairs / self.stats.total_theorems_processed
            )
            self.stats.avg_time_per_theorem = (
                self.stats.total_time_seconds / self.stats.total_theorems_processed
            )
        
        return self.stats
    
    def generate_from_theorems(
        self,
        theorems: List[Any],  # List[lean_dojo.Theorem]
    ) -> DatasetStats:
        """
        Генерирует датасет из списка теорем.
        
        Args:
            theorems: Список LeanDojo Theorem объектов
            
        Returns:
            Статистика генерации
        """
        start_time = time.time()
        
        for i, theorem in enumerate(theorems):
            if len(self.training_pairs) >= self.config.max_total_pairs:
                break
            
            try:
                result, pairs, stats = self._process_theorem(theorem)
                
                self.stats.total_theorems_processed += 1
                if result == ExplorationResult.SUCCESS:
                    self.stats.total_theorems_proved += 1
                
                self._add_pairs(pairs)
                
            except Exception as e:
                logger.warning(f"Error: {e}")
                continue
        
        self.stats.total_time_seconds = time.time() - start_time
        self.stats.total_training_pairs = len(self.training_pairs)
        
        return self.stats
    
    def _process_theorem(self, theorem: Any) -> tuple:
        """Обрабатывает одну теорему."""
        try:
            from lean_dojo import Dojo
        except ImportError:
            raise ImportError("LeanDojo is required")
        
        with Dojo(theorem) as (dojo, state_0):
            return self._explorer.explore(
                dojo,
                state_0,
                theorem_name=theorem.full_name,
                exit_on_proof=False,
            )
    
    def _add_pairs(self, pairs: List[TrainingPair]):
        """Добавляет пары с фильтрацией."""
        for pair in pairs:
            # Фильтрация негативных примеров
            if pair.distance_to_proof < 0:
                if not self.config.include_negative_examples:
                    continue
                
                # Ограничиваем долю негативных
                current_negative_ratio = (
                    self.stats.total_negative_pairs / 
                    max(1, self.stats.total_training_pairs)
                )
                if current_negative_ratio >= self.config.negative_ratio:
                    continue
                
                self.stats.total_negative_pairs += 1
            else:
                self.stats.total_positive_pairs += 1
            
            self.training_pairs.append(pair)
    
    def to_sft_format(self, language: str = "en") -> List[Dict[str, Any]]:
        """
        Конвертирует в SFT формат.
        
        Args:
            language: "en" или "ru"
            
        Returns:
            Список словарей {instruction, input, output}
        """
        if language == "ru":
            instruction = (
                "Сгенерируй следующую тактику Lean 4 для данного состояния доказательства. "
                "Выведи только тактику, без объяснений."
            )
        else:
            instruction = (
                "Generate the next Lean 4 tactic for the given proof state. "
                "Output only the tactic, no explanations."
            )
        
        result = []
        for pair in self.training_pairs:
            result.append({
                "instruction": instruction,
                "input": pair.state,
                "output": pair.tactic,
                "metadata": {
                    "theorem_name": pair.theorem_name,
                    "distance_to_proof": pair.distance_to_proof,
                    "next_state": pair.next_state,
                }
            })
        
        return result
    
    def to_chat_format(self, language: str = "en") -> List[Dict[str, Any]]:
        """
        Конвертирует в Chat формат (messages).
        
        Args:
            language: "en" или "ru"
            
        Returns:
            Список словарей с messages
        """
        if language == "ru":
            system = (
                "Ты — ассистент для доказательства теорем в Lean 4. "
                "Получив состояние доказательства, выведи следующую тактику."
            )
            user_prefix = "Состояние доказательства:\n"
        else:
            system = (
                "You are a Lean 4 theorem proving assistant. "
                "Given a proof state, output the next tactic."
            )
            user_prefix = "Proof state:\n"
        
        result = []
        for pair in self.training_pairs:
            result.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prefix + pair.state},
                    {"role": "assistant", "content": pair.tactic},
                ],
                "metadata": {
                    "theorem_name": pair.theorem_name,
                    "distance_to_proof": pair.distance_to_proof,
                }
            })
        
        return result
    
    def to_raw_pairs(self) -> List[Dict[str, Any]]:
        """Возвращает сырые пары как список словарей."""
        return [pair.to_dict() for pair in self.training_pairs]
    
    def save(
        self,
        output_dir: str,
        format: str = "json",
        language: str = "en",
    ):
        """
        Сохраняет датасет на диск.
        
        Args:
            output_dir: Директория для сохранения
            format: "json", "jsonl", или "all"
            language: Язык для SFT/Chat форматов
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Сохраняем сырые пары
        raw_path = os.path.join(output_dir, "training_pairs.json")
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_raw_pairs(), f, ensure_ascii=False, indent=2)
        logger.info(f"Saved raw pairs to {raw_path}")
        
        # Сохраняем SFT формат
        sft_path = os.path.join(output_dir, "sft_dataset.json")
        with open(sft_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_sft_format(language), f, ensure_ascii=False, indent=2)
        logger.info(f"Saved SFT dataset to {sft_path}")
        
        # Сохраняем Chat формат
        chat_path = os.path.join(output_dir, "chat_dataset.json")
        with open(chat_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_chat_format(language), f, ensure_ascii=False, indent=2)
        logger.info(f"Saved Chat dataset to {chat_path}")
        
        # Сохраняем статистику
        stats_path = os.path.join(output_dir, "stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": self.stats.to_dict(),
                "config": self.config.to_dict(),
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved stats to {stats_path}")
        
        # JSONL формат (для потоковой загрузки)
        if format in ("jsonl", "all"):
            jsonl_path = os.path.join(output_dir, "training_pairs.jsonl")
            with open(jsonl_path, 'w', encoding='utf-8') as f:
                for pair in self.training_pairs:
                    f.write(json.dumps(pair.to_dict(), ensure_ascii=False) + '\n')
            logger.info(f"Saved JSONL to {jsonl_path}")


def generate_lean_dataset(
    repo_url: str,
    commit: str,
    output_dir: str = "./lean_dataset",
    max_theorems: int = 100,
    max_time_per_theorem: int = 60,
    language: str = "en",
    verbose: bool = True,
) -> DatasetStats:
    """
    Удобная функция для генерации датасета.
    
    Args:
        repo_url: URL Lean репозитория
        commit: Коммит
        output_dir: Куда сохранить
        max_theorems: Максимум теорем
        max_time_per_theorem: Секунд на теорему
        language: Язык ("en" или "ru")
        verbose: Подробный вывод
        
    Returns:
        Статистика генерации
        
    Example:
        >>> stats = generate_lean_dataset(
        ...     "https://github.com/leanprover-community/mathlib4",
        ...     "abc123",
        ...     output_dir="./my_dataset",
        ...     max_theorems=50,
        ... )
        >>> print(f"Collected {stats.total_training_pairs} pairs")
    """
    if verbose:
        logging.basicConfig(level=logging.INFO)
    
    config = DatasetConfig(
        repo_url=repo_url,
        repo_commit=commit,
        max_theorems=max_theorems,
        max_time_per_theorem=max_time_per_theorem,
        output_dir=output_dir,
    )
    
    generator = LeanDatasetGenerator(config)
    stats = generator.generate_from_repo(repo_url, commit)
    generator.save(output_dir, language=language)
    
    return stats
