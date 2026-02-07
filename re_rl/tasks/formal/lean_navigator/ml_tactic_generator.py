# re_rl/tasks/formal/ml_tactic_generator.py
"""
ML-based генератор тактик для ускорения BFS.

Использует:
1. HuggingFace модели (локально) — leandojo-lean4-tacgen-byt5-small и др.
2. External API (DeepSeek, OpenAI) — через LeanDojo-v2 ExternalProver
3. Sentence Transformers для embedding-based retrieval

Это УСКОРЯЕТ генерацию данных, но НЕ обязательно.
Базовый TacticGenerator работает без ML.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class MLTacticGenerator(ABC):
    """Базовый класс для ML-генераторов тактик."""
    
    @abstractmethod
    def generate(self, state: str, num_samples: int = 10) -> List[Tuple[str, float]]:
        """
        Генерирует тактики для состояния.
        
        Args:
            state: Pretty-printed proof state
            num_samples: Количество тактик
            
        Returns:
            Список (tactic, score) отсортированный по score
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Проверяет доступность генератора."""
        pass


class HFTacticGenerator(MLTacticGenerator):
    """
    Генератор тактик на основе HuggingFace модели.
    
    Использует модели типа:
    - kaiyuy/leandojo-lean4-tacgen-byt5-small (300MB, быстрая)
    - deepseek-ai/deepseek-prover-v1.5-rl (7B, мощная)
    
    Example:
        >>> gen = HFTacticGenerator("kaiyuy/leandojo-lean4-tacgen-byt5-small")
        >>> tactics = gen.generate("h : p ∧ q\\n⊢ q ∧ p", num_samples=5)
    """
    
    def __init__(
        self,
        model_name: str = "kaiyuy/leandojo-lean4-tacgen-byt5-small",
        device: str = "auto",
        max_length: int = 256,
    ):
        """
        Args:
            model_name: Имя модели на HuggingFace
            device: "auto", "cuda", "cpu"
            max_length: Максимальная длина генерации
        """
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self._model = None
        self._tokenizer = None
        self._available = None
    
    def _load_model(self):
        """Ленивая загрузка модели."""
        if self._model is not None:
            return
        
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            logger.info(f"Loading model: {self.model_name}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # Определяем устройство
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self._model = self._model.to(self.device)
            self._model.eval()
            
            logger.info(f"Model loaded on {self.device}")
            self._available = True
            
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                self._load_model()
            except:
                self._available = False
        return self._available
    
    def generate(self, state: str, num_samples: int = 10) -> List[Tuple[str, float]]:
        """Генерирует тактики используя beam search."""
        if not self.is_available():
            return []
        
        try:
            import torch
            
            # Токенизация
            inputs = self._tokenizer(
                state, 
                return_tensors="pt", 
                truncation=True,
                max_length=512,
            ).to(self.device)
            
            # Генерация с beam search
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_length=self.max_length,
                    num_beams=num_samples * 2,
                    num_return_sequences=num_samples,
                    do_sample=False,
                    return_dict_in_generate=True,
                    output_scores=True,
                )
            
            # Декодирование и scoring
            results = []
            for i, seq in enumerate(outputs.sequences):
                tactic = self._tokenizer.decode(seq, skip_special_tokens=True)
                tactic = tactic.strip()
                
                # Простой score на основе позиции в beam
                score = 1.0 - (i / num_samples)
                
                if tactic:
                    results.append((tactic, score))
            
            return results
            
        except Exception as e:
            logger.warning(f"Generation failed: {e}")
            return []


class ExternalAPITacticGenerator(MLTacticGenerator):
    """
    Генератор тактик через внешний API.
    
    Поддерживает:
    - DeepSeek API
    - OpenAI API  
    - LeanDojo-v2 ExternalProver
    
    Example:
        >>> gen = ExternalAPITacticGenerator(
        ...     api_url="https://api.deepseek.com/v1/chat/completions",
        ...     api_key="sk-...",
        ...     model="deepseek-prover-v2"
        ... )
        >>> tactics = gen.generate(state)
    """
    
    def __init__(
        self,
        api_url: str = "",
        api_key: str = "",
        model: str = "deepseek-prover-v2",
        temperature: float = 0.0,
        max_tokens: int = 256,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._available = None
    
    def is_available(self) -> bool:
        if self._available is None:
            self._available = bool(self.api_url and self.api_key)
        return self._available
    
    def generate(self, state: str, num_samples: int = 10) -> List[Tuple[str, float]]:
        """Генерирует тактики через API."""
        if not self.is_available():
            return []
        
        try:
            import requests
            
            prompt = self._build_prompt(state)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a Lean 4 theorem prover. Output only the tactic, nothing else."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "n": num_samples,
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            
            tactics = []
            for i, choice in enumerate(result.get("choices", [])):
                content = choice.get("message", {}).get("content", "")
                tactic = content.strip()
                score = 1.0 - (i / max(1, len(result["choices"])))
                if tactic:
                    tactics.append((tactic, score))
            
            return tactics
            
        except Exception as e:
            logger.warning(f"API call failed: {e}")
            return []
    
    def _build_prompt(self, state: str) -> str:
        return f"Generate the next Lean 4 tactic for this proof state:\n\n{state}\n\nTactic:"


class LeanDojoProverGenerator(MLTacticGenerator):
    """
    Генератор тактик через LeanDojo-v2 provers.
    
    Использует HFProver или ExternalProver из LeanDojo-v2.
    
    Example:
        >>> gen = LeanDojoProverGenerator(prover_type="hf")
        >>> tactics = gen.generate(state)
    """
    
    def __init__(
        self,
        prover_type: str = "hf",  # "hf" или "external"
        model_name: str = "kaiyuy/leandojo-lean4-tacgen-byt5-small",
        **prover_kwargs,
    ):
        self.prover_type = prover_type
        self.model_name = model_name
        self.prover_kwargs = prover_kwargs
        self._prover = None
        self._available = None
    
    def _load_prover(self):
        if self._prover is not None:
            return
        
        try:
            if self.prover_type == "hf":
                from lean_dojo_v2.prover import HFProver
                self._prover = HFProver(model_name=self.model_name, **self.prover_kwargs)
            else:
                from lean_dojo_v2.prover import ExternalProver
                self._prover = ExternalProver(**self.prover_kwargs)
            
            self._available = True
            
        except ImportError:
            logger.warning("LeanDojo-v2 not available")
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to load prover: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                self._load_prover()
            except:
                self._available = False
        return self._available
    
    def generate(self, state: str, num_samples: int = 10) -> List[Tuple[str, float]]:
        if not self.is_available():
            return []
        
        try:
            tactics = self._prover.generate_tactics(state, num_samples=num_samples)
            
            # Преобразуем в формат (tactic, score)
            results = []
            for i, tactic in enumerate(tactics):
                score = 1.0 - (i / max(1, len(tactics)))
                results.append((tactic, score))
            
            return results
            
        except Exception as e:
            logger.warning(f"Prover generation failed: {e}")
            return []


class EmbeddingTacticRetriever(MLTacticGenerator):
    """
    Retrieval-based генератор как в LeanNavigator.
    
    Использует sentence-transformers для эмбеддингов
    и FAISS для быстрого поиска похожих тактик.
    
    Это самый близкий к оригинальному LeanNavigator подход.
    
    Example:
        >>> retriever = EmbeddingTacticRetriever()
        >>> retriever.build_index(tactic_templates)  # Один раз
        >>> tactics = retriever.generate(state)
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_path: Optional[str] = None,
    ):
        self.model_name = model_name
        self.index_path = index_path
        self._model = None
        self._index = None
        self._tactics = []
        self._available = None
    
    def _load_model(self):
        if self._model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            self._available = True
            
        except ImportError:
            logger.warning("sentence-transformers not installed")
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                self._load_model()
            except:
                self._available = False
        return self._available
    
    def build_index(self, tactics: List[str]):
        """
        Строит FAISS индекс для списка тактик.
        
        Args:
            tactics: Список шаблонов тактик
        """
        if not self.is_available():
            return
        
        try:
            import faiss
            import numpy as np
            
            logger.info(f"Building index for {len(tactics)} tactics")
            
            self._tactics = tactics
            
            # Получаем эмбеддинги
            embeddings = self._model.encode(tactics, show_progress_bar=True)
            embeddings = np.array(embeddings).astype('float32')
            
            # Строим FAISS индекс
            dimension = embeddings.shape[1]
            self._index = faiss.IndexFlatL2(dimension)
            self._index.add(embeddings)
            
            logger.info(f"Index built with {self._index.ntotal} vectors")
            
        except ImportError:
            logger.warning("faiss not installed. Install with: pip install faiss-cpu")
        except Exception as e:
            logger.warning(f"Failed to build index: {e}")
    
    def save_index(self, path: str):
        """Сохраняет индекс на диск."""
        if self._index is None:
            return
        
        try:
            import faiss
            import json
            
            faiss.write_index(self._index, f"{path}.index")
            with open(f"{path}.tactics.json", 'w') as f:
                json.dump(self._tactics, f)
                
        except Exception as e:
            logger.warning(f"Failed to save index: {e}")
    
    def load_index(self, path: str):
        """Загружает индекс с диска."""
        try:
            import faiss
            import json
            
            self._index = faiss.read_index(f"{path}.index")
            with open(f"{path}.tactics.json", 'r') as f:
                self._tactics = json.load(f)
                
        except Exception as e:
            logger.warning(f"Failed to load index: {e}")
    
    def generate(self, state: str, num_samples: int = 100) -> List[Tuple[str, float]]:
        """Находит похожие тактики через поиск по эмбеддингам."""
        if not self.is_available() or self._index is None:
            return []
        
        try:
            import numpy as np
            
            # Эмбеддинг состояния
            query_embedding = self._model.encode([state])
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Поиск ближайших
            distances, indices = self._index.search(query_embedding, num_samples)
            
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self._tactics):
                    tactic = self._tactics[idx]
                    # Конвертируем расстояние в score (меньше = лучше)
                    score = 1.0 / (1.0 + dist)
                    results.append((tactic, score))
            
            return sorted(results, key=lambda x: -x[1])
            
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []


class HybridTacticGenerator(MLTacticGenerator):
    """
    Гибридный генератор: комбинирует ML и rule-based подходы.
    
    1. Сначала пробует ML генератор
    2. Дополняет rule-based тактиками
    3. Убирает дубликаты
    
    Example:
        >>> hybrid = HybridTacticGenerator(
        ...     ml_generator=HFTacticGenerator(),
        ...     fallback_to_rules=True,
        ... )
        >>> tactics = hybrid.generate(state)
    """
    
    def __init__(
        self,
        ml_generator: Optional[MLTacticGenerator] = None,
        fallback_to_rules: bool = True,
        ml_weight: float = 0.7,  # Вес ML тактик
    ):
        self.ml_generator = ml_generator
        self.fallback_to_rules = fallback_to_rules
        self.ml_weight = ml_weight
        self._rule_generator = None
    
    def _get_rule_generator(self):
        if self._rule_generator is None:
            from .tactic_generator import TacticGenerator
            self._rule_generator = TacticGenerator()
        return self._rule_generator
    
    def is_available(self) -> bool:
        # Всегда доступен (fallback на rules)
        return True
    
    def generate(self, state: str, num_samples: int = 100) -> List[Tuple[str, float]]:
        results = []
        seen = set()
        
        # 1. ML тактики
        if self.ml_generator and self.ml_generator.is_available():
            ml_tactics = self.ml_generator.generate(state, num_samples=num_samples // 2)
            for tactic, score in ml_tactics:
                if tactic not in seen:
                    results.append((tactic, score * self.ml_weight))
                    seen.add(tactic)
        
        # 2. Rule-based тактики
        if self.fallback_to_rules:
            rule_gen = self._get_rule_generator()
            rule_tactics = rule_gen.generate(state)
            
            for i, tactic in enumerate(rule_tactics):
                if tactic not in seen:
                    score = (1.0 - self.ml_weight) * (1.0 - i / max(1, len(rule_tactics)))
                    results.append((tactic, score))
                    seen.add(tactic)
        
        # Сортируем по score
        results.sort(key=lambda x: -x[1])
        return results[:num_samples]


def create_ml_generator(
    generator_type: str = "hybrid",
    model_name: Optional[str] = None,
    **kwargs,
) -> MLTacticGenerator:
    """
    Фабрика для создания ML генераторов.
    
    Args:
        generator_type: "hf", "api", "leandojo", "embedding", "hybrid"
        model_name: Имя модели (зависит от типа)
        **kwargs: Дополнительные аргументы
        
    Returns:
        Экземпляр MLTacticGenerator
        
    Example:
        >>> gen = create_ml_generator("hf", model_name="kaiyuy/leandojo-lean4-tacgen-byt5-small")
        >>> gen = create_ml_generator("hybrid")  # ML + rules fallback
    """
    if generator_type == "hf":
        return HFTacticGenerator(
            model_name=model_name or "kaiyuy/leandojo-lean4-tacgen-byt5-small",
            **kwargs,
        )
    
    elif generator_type == "api":
        return ExternalAPITacticGenerator(**kwargs)
    
    elif generator_type == "leandojo":
        return LeanDojoProverGenerator(
            model_name=model_name or "kaiyuy/leandojo-lean4-tacgen-byt5-small",
            **kwargs,
        )
    
    elif generator_type == "embedding":
        return EmbeddingTacticRetriever(
            model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2",
            **kwargs,
        )
    
    elif generator_type == "hybrid":
        ml_gen = None
        if model_name:
            ml_gen = HFTacticGenerator(model_name=model_name)
        return HybridTacticGenerator(ml_generator=ml_gen, **kwargs)
    
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")
