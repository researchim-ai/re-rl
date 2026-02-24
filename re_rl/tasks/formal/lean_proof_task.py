# re_rl/tasks/formal/lean_proof_task.py
"""
Генератор задач на формальные доказательства в Lean 4.

Поддерживает:
- Шаблонную генерацию (без LLM) — верифицируемые доказательства
- Генерацию через LeanDojo provers (если доступно)
- Экспорт в SFT-формат
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, ClassVar, Literal
import random

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template

from .theorem_templates import (
    TheoremTemplate,
    THEOREM_TEMPLATES,
    get_random_template,
    get_theorem_categories,
)


# Категории теорем с привязкой к сложности
DIFFICULTY_TO_CATEGORIES: Dict[int, List[str]] = {
    1: ["propositional"],
    2: ["propositional", "equality"],
    3: ["propositional", "equality", "predicate", "list"],
    4: ["predicate", "nat_arithmetic", "list"],
    5: ["nat_arithmetic", "list"],
    6: ["nat_arithmetic", "list"],
    7: ["nat_arithmetic", "list"],
    8: ["nat_arithmetic", "list"],
    9: ["nat_arithmetic", "list"],
    10: ["nat_arithmetic", "list"],
}


@dataclass
class LeanProofTask(BaseMathTask):
    """
    Задача: доказать теорему в Lean 4.
    
    Attributes:
        theorem_statement: Формулировка теоремы на Lean 4
        proof: Доказательство (тактики)
        category: Категория теоремы (propositional, nat_arithmetic, etc.)
        use_llm: Если True, пытается использовать LeanDojo prover
        
    Example:
        >>> task = LeanProofTask.from_difficulty(3, language="ru")
        >>> task.solve()
        >>> print(task.get_result())
    """
    
    TASK_TYPE: ClassVar[str] = "lean_proof"
    
    # Пресеты сложности
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_tactics": 2, "categories": ["propositional"]},
        3: {"max_tactics": 4, "categories": ["propositional", "equality", "predicate"]},
        5: {"max_tactics": 6, "categories": ["nat_arithmetic", "list"]},
        7: {"max_tactics": 8, "categories": ["nat_arithmetic", "list"]},
        10: {"max_tactics": 15, "categories": ["nat_arithmetic", "list"]},
    }
    
    # Поля задачи
    theorem_statement: str = ""
    proof: str = ""
    category: str = "propositional"
    theorem_name: str = ""
    use_llm: bool = False  # Использовать LLM для генерации (по умолчанию — шаблоны)
    
    # Внутренние поля
    _template: Optional[TheoremTemplate] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Инициализация задачи из шаблона или параметров."""
        if not self.theorem_statement and not self._template:
            # Генерируем из шаблона по категории
            self._template = get_random_template(
                category=self.category,
                min_difficulty=1,
                max_difficulty=10,
            )
            self._init_from_template()
        elif self._template:
            self._init_from_template()
    
    def _init_from_template(self):
        """Инициализирует поля из шаблона."""
        if not self._template:
            return
        
        # Получаем конкретный экземпляр (с параметрами)
        template = self._template.get_random_instance()
        
        self.theorem_name = template.name
        self.theorem_statement = template.theorem
        self.proof = template.proof
        self.category = template.category
        
        # Формулировка на естественном языке
        lang = self.language if self.language in template.natural_statement else "en"
        self.description = template.natural_statement.get(lang, template.natural_statement.get("en", ""))
    
    @classmethod
    def from_difficulty(
        cls,
        difficulty: int,
        language: str = "ru",
        detail_level: int = 3,
        category: Optional[str] = None,
        **overrides
    ) -> "LeanProofTask":
        """
        Создаёт задачу с заданным уровнем сложности.
        
        Args:
            difficulty: Уровень сложности (1-10)
            language: Язык ("ru" или "en")
            detail_level: Уровень детализации решения
            category: Категория теоремы (если None — выбирается по сложности)
            **overrides: Дополнительные параметры
            
        Returns:
            Экземпляр LeanProofTask
        """
        difficulty = max(1, min(10, difficulty))
        
        # Определяем категорию по сложности
        if category is None:
            available_categories = DIFFICULTY_TO_CATEGORIES.get(difficulty, ["propositional"])
            category = random.choice(available_categories)
        
        # Находим подходящий шаблон
        # Расширяем диапазон, если нет шаблонов
        min_diff = max(1, difficulty - 2)
        max_diff = min(10, difficulty + 2)
        
        try:
            template = get_random_template(
                category=category,
                min_difficulty=min_diff,
                max_difficulty=max_diff,
            )
        except ValueError:
            # Если нет шаблона для комбинации — пробуем без ограничения категории
            # или расширяем диапазон сложности
            try:
                template = get_random_template(
                    category=category,
                    min_difficulty=1,
                    max_difficulty=10,
                )
            except ValueError:
                # Fallback — любой шаблон
                template = get_random_template(
                    category=None,
                    min_difficulty=min_diff,
                    max_difficulty=max_diff,
                )
        
        return cls(
            description="",  # Будет заполнено из шаблона
            language=language,
            detail_level=detail_level,
            category=category,
            _template=template,
        )
    
    @classmethod
    def from_template(
        cls,
        template: TheoremTemplate,
        language: str = "ru",
        detail_level: int = 3,
    ) -> "LeanProofTask":
        """Создаёт задачу из конкретного шаблона."""
        return cls(
            description="",
            language=language,
            detail_level=detail_level,
            category=template.category,
            _template=template,
        )
    
    def solve(self):
        """
        Генерирует решение (доказательство).
        
        Использует:
        1. Шаблонное доказательство (по умолчанию)
        2. LeanDojo prover (если use_llm=True и доступен)
        """
        if self.use_llm:
            self._solve_with_llm()
        else:
            self._solve_from_template()
    
    def _solve_from_template(self):
        """Использует доказательство из шаблона."""
        if not self.proof:
            raise ValueError("No proof available in template")
        
        # Парсим тактики как шаги решения
        self.solution_steps = self._parse_proof_to_steps(self.proof)
        self.final_answer = self.proof
        
        # Добавляем объяснения из шаблона
        if self._template:
            lang = self.language if self.language in self._template.natural_proof else "en"
            explanation = self._template.natural_proof.get(lang, "")
            if explanation:
                self.explanation_steps = [explanation]
    
    def _solve_with_llm(self):
        """Генерирует доказательство через LeanDojo prover."""
        try:
            from lean_dojo_v2.prover import ExternalProver
            
            prover = ExternalProver()
            proof = prover.generate_whole_proof(self.theorem_statement)
            
            self.proof = proof
            self.solution_steps = self._parse_proof_to_steps(proof)
            self.final_answer = proof
            
        except ImportError:
            # Fallback к шаблону
            self._solve_from_template()
        except Exception as e:
            # При ошибке API — fallback к шаблону
            self._solve_from_template()
    
    def _parse_proof_to_steps(self, proof: str) -> List[str]:
        """
        Разбирает доказательство на шаги.
        
        Args:
            proof: Строка с тактиками
            
        Returns:
            Список шагов решения
        """
        lines = proof.strip().split('\n')
        steps = []
        
        tactic_label = get_template(PROMPT_TEMPLATES["inline"], "tactic_label", self.language, augment=False)
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('--'):  # Пропускаем комментарии
                steps.append(f"{tactic_label} {i}: {line}")
        
        return steps
    
    def generate_prompt(self) -> str:
        """Генерирует промпт для модели."""
        return get_template(
            PROMPT_TEMPLATES["inline"],
            "lean_prove_theorem_prompt",
            self.language,
            augment=False,
            theorem=self.theorem_statement,
        )
    
    def get_result(self) -> Dict[str, Any]:
        """Возвращает структуру результата для обучения."""
        if not self.solution_steps or not self.final_answer:
            self.solve()
        
        result = {
            "task_type": self.TASK_TYPE,
            "problem": self.description,
            "language": self.language,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer,
            
            # Дополнительные поля для formal math
            "theorem_statement": self.theorem_statement,
            "proof": self.proof,
            "category": self.category,
            "theorem_name": self.theorem_name,
        }
        
        if self.explanation_steps:
            result["explanations"] = self.explanation_steps
        
        return result
    
    def to_sft_format(self) -> Dict[str, Any]:
        """
        Конвертирует в SFT-формат (instruction/input/output).
        
        Returns:
            Словарь в формате для SFT обучения
        """
        if not self.final_answer:
            self.solve()
        
        instruction = get_template(
            PROMPT_TEMPLATES["inline"],
            "lean_sft_instruction",
            self.language,
            augment=False,
        )
        
        return {
            "instruction": instruction,
            "input": self.theorem_statement,
            "output": self.proof,
            "metadata": {
                "task_type": self.TASK_TYPE,
                "category": self.category,
                "theorem_name": self.theorem_name,
                "language": self.language,
                "difficulty": self._template.difficulty if self._template else 1,
            }
        }
    
    def to_chat_format(self) -> Dict[str, Any]:
        """
        Конвертирует в Chat-формат (messages).
        
        Returns:
            Словарь с messages в формате ChatML
        """
        if not self.final_answer:
            self.solve()
        
        system_msg = get_template(
            PROMPT_TEMPLATES["inline"],
            "lean_chat_system",
            self.language,
            augment=False,
        )
        user_msg = get_template(
            PROMPT_TEMPLATES["inline"],
            "lean_chat_user",
            self.language,
            augment=False,
            theorem=self.theorem_statement,
        )
        
        return {
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": self.proof},
            ],
            "metadata": {
                "task_type": self.TASK_TYPE,
                "category": self.category,
                "theorem_name": self.theorem_name,
            }
        }


def generate_lean_proof_task(
    difficulty: int = 5,
    language: str = "ru",
    category: Optional[str] = None,
    detail_level: int = 3,
) -> LeanProofTask:
    """
    Генерирует случайную задачу на доказательство теоремы.
    
    Args:
        difficulty: Уровень сложности (1-10)
        language: Язык ("ru" или "en")
        category: Категория теоремы (если None — случайная по сложности)
        detail_level: Уровень детализации
        
    Returns:
        Экземпляр LeanProofTask
        
    Example:
        >>> task = generate_lean_proof_task(difficulty=3, language="ru")
        >>> task.solve()
        >>> print(task.to_sft_format())
    """
    return LeanProofTask.from_difficulty(
        difficulty=difficulty,
        language=language,
        category=category,
        detail_level=detail_level,
    )


def generate_lean_proof_batch(
    num_samples: int,
    difficulties: Optional[List[int]] = None,
    categories: Optional[List[str]] = None,
    language: str = "ru",
) -> List[LeanProofTask]:
    """
    Генерирует batch задач для датасета.
    
    Args:
        num_samples: Количество задач
        difficulties: Список сложностей (если None — случайные 1-10)
        categories: Список категорий (если None — все)
        language: Язык
        
    Returns:
        Список LeanProofTask
    """
    if difficulties is None:
        difficulties = list(range(1, 11))
    
    if categories is None:
        categories = get_theorem_categories()
    
    tasks = []
    for _ in range(num_samples):
        difficulty = random.choice(difficulties)
        category = random.choice(categories)
        
        try:
            task = LeanProofTask.from_difficulty(
                difficulty=difficulty,
                language=language,
                category=category,
            )
            task.solve()
            tasks.append(task)
        except ValueError:
            # Если нет шаблона для комбинации — пробуем другую
            task = LeanProofTask.from_difficulty(
                difficulty=difficulty,
                language=language,
                category=None,  # Автовыбор
            )
            task.solve()
            tasks.append(task)
    
    return tasks
