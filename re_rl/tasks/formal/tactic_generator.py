# re_rl/tasks/formal/tactic_generator.py
"""
Генератор тактик Lean 4 без использования ML.

Использует:
- Хардкодный список базовых тактик
- Парсинг состояния для извлечения гипотез/переменных
- Подстановку переменных в шаблоны тактик
"""

from typing import List, Set, Optional, Iterator
from dataclasses import dataclass
import itertools

from .lean_utils import (
    extract_hypotheses,
    extract_variables,
    extract_goal,
    classify_lean_elements,
    LEAN4_TACTICS,
)


@dataclass
class TacticTemplate:
    """Шаблон тактики с плейсхолдерами."""
    template: str
    requires_hypothesis: bool = False
    requires_variable: bool = False
    max_instantiations: int = 10  # Макс. количество инстанциаций


# Шаблоны тактик с плейсхолдерами
TACTIC_TEMPLATES: List[TacticTemplate] = [
    # === Завершающие тактики (без аргументов) ===
    TacticTemplate("rfl"),
    TacticTemplate("trivial"),
    TacticTemplate("decide"),
    TacticTemplate("assumption"),
    TacticTemplate("contradiction"),
    TacticTemplate("done"),
    
    # === Автоматические тактики ===
    TacticTemplate("simp"),
    TacticTemplate("simp_all"),
    TacticTemplate("norm_num"),
    TacticTemplate("norm_cast"),
    TacticTemplate("ring"),
    TacticTemplate("ring_nf"),
    TacticTemplate("linarith"),
    TacticTemplate("nlinarith"),
    TacticTemplate("omega"),
    TacticTemplate("aesop"),
    TacticTemplate("tauto"),
    TacticTemplate("positivity"),
    TacticTemplate("field_simp"),
    
    # === Структурные тактики ===
    TacticTemplate("intro h"),
    TacticTemplate("intro x"),
    TacticTemplate("intros"),
    TacticTemplate("constructor"),
    TacticTemplate("left"),
    TacticTemplate("right"),
    TacticTemplate("existsi {h}", requires_hypothesis=True),
    TacticTemplate("use {h}", requires_hypothesis=True),
    
    # === Тактики с гипотезой ===
    TacticTemplate("exact {h}", requires_hypothesis=True),
    TacticTemplate("apply {h}", requires_hypothesis=True),
    TacticTemplate("refine {h}", requires_hypothesis=True),
    TacticTemplate("cases {h}", requires_hypothesis=True),
    TacticTemplate("rcases {h} with ⟨_, _⟩", requires_hypothesis=True),
    TacticTemplate("obtain ⟨a, b⟩ := {h}", requires_hypothesis=True),
    TacticTemplate("induction {h}", requires_hypothesis=True),
    TacticTemplate("specialize {h}", requires_hypothesis=True),
    
    # === Переписывание ===
    TacticTemplate("rw [{h}]", requires_hypothesis=True),
    TacticTemplate("rw [← {h}]", requires_hypothesis=True),
    TacticTemplate("simp [{h}]", requires_hypothesis=True),
    TacticTemplate("simp only [{h}]", requires_hypothesis=True),
    TacticTemplate("simp_rw [{h}]", requires_hypothesis=True),
    
    # === Логические ===
    TacticTemplate("exfalso"),
    TacticTemplate("by_contra h"),
    TacticTemplate("by_cases h : {h}", requires_hypothesis=True),
    TacticTemplate("push_neg"),
    TacticTemplate("contrapose"),
    
    # === Равенство ===
    TacticTemplate("symm"),
    TacticTemplate("trans"),
    TacticTemplate("congr"),
    TacticTemplate("funext"),
    TacticTemplate("ext"),
    TacticTemplate("ext x"),
    
    # === Составные тактики ===
    TacticTemplate("simp; ring"),
    TacticTemplate("simp; linarith"),
    TacticTemplate("constructor <;> simp"),
    TacticTemplate("intro h; exact h"),
    TacticTemplate("intro h; apply {h}", requires_hypothesis=True),
    
    # === have/let ===
    TacticTemplate("have h := {h}", requires_hypothesis=True),
    TacticTemplate("let x := {h}", requires_hypothesis=True),
    
    # === Специальные комбинации ===
    TacticTemplate("first | rfl | simp | ring"),
    TacticTemplate("try simp"),
    TacticTemplate("try ring"),
    TacticTemplate("all_goals simp"),
    
    # === Тактики с переменными ===
    TacticTemplate("induction {v} with | zero => _ | succ n ih => _", requires_variable=True),
    TacticTemplate("cases {v}", requires_variable=True),
]


# Дополнительные тактики для конкретных паттернов в goal
GOAL_PATTERN_TACTICS = {
    # Если цель — равенство
    "=": ["rfl", "ring", "simp", "norm_num", "congr", "ext"],
    
    # Если цель — неравенство
    "≤": ["linarith", "omega", "norm_num", "simp"],
    "≥": ["linarith", "omega", "norm_num", "simp"],
    "<": ["linarith", "omega", "norm_num", "simp"],
    ">": ["linarith", "omega", "norm_num", "simp"],
    "≠": ["simp", "omega", "norm_num", "contradiction"],
    
    # Если цель — конъюнкция
    "∧": ["constructor", "And.intro"],
    
    # Если цель — дизъюнкция
    "∨": ["left", "right", "Or.inl", "Or.inr"],
    
    # Если цель — импликация
    "→": ["intro h", "intro", "fun h =>"],
    
    # Если цель — отрицание
    "¬": ["intro h", "by_contra h", "push_neg"],
    
    # Если цель — квантор всеобщности
    "∀": ["intro", "intros"],
    
    # Если цель — квантор существования
    "∃": ["use", "existsi", "refine ⟨_, _⟩"],
    
    # Если цель — True
    "True": ["trivial", "constructor"],
    
    # Если цель — False  
    "False": ["contradiction", "exfalso", "absurd"],
    
    # Если цель — iff
    "↔": ["constructor", "Iff.intro"],
    
    # Если цель содержит Nat
    "Nat": ["omega", "norm_num", "simp", "induction"],
    
    # Если цель содержит List
    "List": ["simp", "induction", "cases"],
}


class TacticGenerator:
    """
    Генератор тактик на основе состояния доказательства.
    
    Не использует ML — только эвристики и подстановки.
    """
    
    def __init__(
        self,
        templates: Optional[List[TacticTemplate]] = None,
        max_tactics_per_template: int = 5,
        use_goal_patterns: bool = True,
    ):
        """
        Args:
            templates: Список шаблонов тактик (по умолчанию — TACTIC_TEMPLATES)
            max_tactics_per_template: Макс. тактик на шаблон
            use_goal_patterns: Использовать паттерны в цели для приоритизации
        """
        self.templates = templates or TACTIC_TEMPLATES
        self.max_per_template = max_tactics_per_template
        self.use_goal_patterns = use_goal_patterns
    
    def generate(self, state: str) -> List[str]:
        """
        Генерирует список тактик для данного состояния.
        
        Args:
            state: Pretty-printed proof state
            
        Returns:
            Список тактик для попробовать
        """
        tactics: List[str] = []
        seen: Set[str] = set()
        
        # Извлекаем информацию из состояния
        hypotheses = extract_hypotheses(state)
        variables = extract_variables(state)
        goal = extract_goal(state)
        
        # 1. Добавляем тактики на основе паттернов в goal
        if self.use_goal_patterns and goal:
            for pattern, pattern_tactics in GOAL_PATTERN_TACTICS.items():
                if pattern in goal:
                    for t in pattern_tactics:
                        if t not in seen:
                            tactics.append(t)
                            seen.add(t)
        
        # 2. Генерируем тактики из шаблонов
        for template in self.templates:
            for tactic in self._instantiate_template(template, hypotheses, variables):
                if tactic not in seen:
                    tactics.append(tactic)
                    seen.add(tactic)
        
        return tactics
    
    def _instantiate_template(
        self,
        template: TacticTemplate,
        hypotheses: List[str],
        variables: List[str],
    ) -> Iterator[str]:
        """
        Инстанцирует шаблон тактики с конкретными значениями.
        
        Args:
            template: Шаблон тактики
            hypotheses: Доступные гипотезы
            variables: Доступные переменные
            
        Yields:
            Конкретные тактики
        """
        t = template.template
        
        # Если нет плейсхолдеров — возвращаем как есть
        if '{h}' not in t and '{v}' not in t:
            yield t
            return
        
        # Подставляем гипотезы
        if '{h}' in t:
            if not hypotheses:
                return
            
            count = 0
            for h in hypotheses[:template.max_instantiations]:
                yield t.replace('{h}', h)
                count += 1
                if count >= self.max_per_template:
                    break
        
        # Подставляем переменные
        elif '{v}' in t:
            if not variables:
                return
            
            count = 0
            for v in variables[:template.max_instantiations]:
                yield t.replace('{v}', v)
                count += 1
                if count >= self.max_per_template:
                    break


def generate_tactics(state: str, max_count: int = 200) -> List[str]:
    """
    Генерирует тактики для состояния.
    
    Args:
        state: Pretty-printed proof state
        max_count: Максимальное количество тактик
        
    Returns:
        Список тактик
        
    Example:
        >>> state = "h : p ∧ q\\n⊢ q ∧ p"
        >>> tactics = generate_tactics(state)
        >>> print(tactics[:5])
        ['constructor', 'exact ⟨h.2, h.1⟩', 'exact h', ...]
    """
    generator = TacticGenerator()
    tactics = generator.generate(state)
    return tactics[:max_count]


def generate_tactics_for_goal(goal: str) -> List[str]:
    """
    Генерирует тактики специфичные для данной цели.
    
    Args:
        goal: Цель (target) доказательства
        
    Returns:
        Список тактик
    """
    tactics = []
    
    for pattern, pattern_tactics in GOAL_PATTERN_TACTICS.items():
        if pattern in goal:
            tactics.extend(pattern_tactics)
    
    # Дедупликация с сохранением порядка
    seen = set()
    result = []
    for t in tactics:
        if t not in seen:
            result.append(t)
            seen.add(t)
    
    return result
