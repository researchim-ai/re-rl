# re_rl/tasks/formal/lean_utils.py
"""
Утилиты для работы с Lean 4 состояниями и тактиками.

Адаптировано из LeanNavigator (lean_math_utils.py).
"""

import re
import heapq
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass


# Паттерн для идентификаторов Lean
VARIABLE_PATTERN = r'[a-zA-Z_\'\u03b1-\u03c9][a-zA-Z_\'\u03b1-\u03c9\d₀-₉]*'

# Базовые тактики Lean 4
LEAN4_TACTICS = [
    # Завершающие тактики
    "rfl", "trivial", "decide", "native_decide", "rfl'",
    
    # Автоматические тактики  
    "simp", "simp_all", "simp only", "norm_num", "norm_cast",
    "ring", "ring_nf", "linarith", "nlinarith", "omega", "aesop",
    "tauto", "decide", "positivity", "polyrith", "field_simp",
    
    # Структурные тактики
    "intro", "intros", "constructor", "left", "right",
    "cases", "rcases", "obtain", "induction", "match",
    "exact", "apply", "refine", "have", "let", "use", "existsi",
    
    # Переписывание
    "rw", "rewrite", "simp_rw", "conv", "calc",
    "erw", "nth_rw", "conv_lhs", "conv_rhs",
    
    # Манипуляции с контекстом
    "clear", "rename", "revert", "specialize", "generalize",
    
    # Логические
    "exfalso", "contradiction", "by_contra", "by_cases", "push_neg",
    "contrapose", "absurd",
    
    # Равенство
    "symm", "trans", "congr", "funext", "ext", "ext1",
    
    # Индукция и рекурсия
    "induction", "cases", "match", "split_ifs",
    
    # Специальные
    "assumption", "trivial", "done",  # sorry намеренно исключён — unsound
    "all_goals", "any_goals", "focus", "swap", "rotate",
]

# Ключевые слова Lean 4
LEAN4_KEYWORDS = [
    "abbrev", "axiom", "by", "calc", "class", "def", "deriving",
    "do", "else", "end", "example", "export", "extends", "for",
    "fun", "if", "import", "in", "inductive", "infix", "infixl",
    "infixr", "instance", "let", "macro", "match", "mutual",
    "namespace", "notation", "opaque", "open", "partial", "prefix",
    "private", "protected", "return", "scoped", "section", "set_option",
    "structure", "syntax", "theorem", "universe", "variable", "where", "with",
]


@dataclass
class ProofState:
    """Представление состояния доказательства."""
    pp: str  # Pretty-printed state
    goals: List[str]  # Список целей (targets)
    hypotheses: Dict[str, str]  # name -> type
    
    @classmethod
    def from_pp(cls, pp: str) -> "ProofState":
        """Создаёт ProofState из pretty-printed строки."""
        goals = []
        hypotheses = {}
        
        for line in pp.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('⊢'):
                # Это цель
                goals.append(line[1:].strip())
            elif ':' in line and not line.startswith('case'):
                # Это гипотеза
                parts = line.split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    type_info = parts[1].strip()
                    # Может быть несколько имён через пробел
                    for n in name.split():
                        hypotheses[n] = type_info
        
        return cls(pp=pp, goals=goals, hypotheses=hypotheses)


def classify_lean_element(line: str) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
    """
    Классифицирует элемент Lean состояния.
    
    Returns:
        (category, names, type_info) или (None, None, None)
    """
    VARIABLE_TYPES = ['ℝ', 'ℕ', 'ℤ', 'ℚ', 'ℂ', 'Bool', 'Nat', 'Int', 'Prop']
    
    line = line.strip()
    if not line:
        return None, None, None
    
    # Пропускаем case labels
    if line.startswith('case '):
        return None, None, None
    
    # Разделяем по ':'
    parts = line.split(':', 1)
    if len(parts) != 2:
        return None, None, None
    
    name_part, type_info = parts[0].strip(), parts[1].strip()
    
    # Классификация по типу
    if type_info.startswith('Type') or type_info.startswith('Sort'):
        return 'type', name_part.split(), type_info
    
    if type_info.startswith('Set'):
        return 'set', name_part.split(), type_info
    
    if type_info.startswith(('∀', '∃', '¬')):
        return 'hypothesis', name_part.split(), type_info
    
    if any(type_info == t or type_info.startswith(t + ' ') for t in VARIABLE_TYPES):
        return 'variable', name_part.split(), type_info
    
    # Функции или гипотезы с →
    if '→' in type_info or 'fun' in type_info or ':=' in type_info:
        if '∀' in type_info or '∃' in type_info:
            return 'hypothesis', name_part.split(), type_info
        return 'function', name_part.split(), type_info
    
    # Пропозиции
    if 'Prop' in type_info or '¬' in type_info or '∈' in type_info or '∉' in type_info:
        return 'hypothesis', name_part.split(), type_info
    
    # По умолчанию — unknown
    return 'unknown', name_part.split(), type_info


def classify_lean_elements(lean_state: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Классифицирует все элементы в Lean состоянии.
    
    Args:
        lean_state: Pretty-printed состояние
        
    Returns:
        (category_of_name, type_info_of_name)
    """
    category_of_name = {}
    type_info_of_name = {}
    
    for line in lean_state.strip().split('\n'):
        category, names, type_info = classify_lean_element(line)
        if category is None or names is None:
            continue
        
        for name in names:
            category_of_name[name] = category
            type_info_of_name[name] = type_info
    
    # Разрешаем unknown переменные через типы
    for name in list(category_of_name.keys()):
        if category_of_name[name] == 'unknown':
            type_info = type_info_of_name[name]
            if type_info in category_of_name and category_of_name[type_info] == 'type':
                category_of_name[name] = 'variable'
    
    return category_of_name, type_info_of_name


def extract_hypotheses(state: str) -> List[str]:
    """
    Извлекает имена гипотез из состояния.
    
    Args:
        state: Pretty-printed состояние
        
    Returns:
        Список имён гипотез
    """
    category_of_name, _ = classify_lean_elements(state)
    return [name for name, cat in category_of_name.items() 
            if cat in ('hypothesis', 'function', 'unknown')]


def extract_variables(state: str) -> List[str]:
    """
    Извлекает имена переменных из состояния.
    
    Args:
        state: Pretty-printed состояние
        
    Returns:
        Список имён переменных
    """
    category_of_name, _ = classify_lean_elements(state)
    return [name for name, cat in category_of_name.items() 
            if cat == 'variable']


def extract_goal(state: str) -> Optional[str]:
    """
    Извлекает первую цель из состояния.
    
    Args:
        state: Pretty-printed состояние
        
    Returns:
        Цель или None
    """
    for line in state.strip().split('\n'):
        line = line.strip()
        if line.startswith('⊢'):
            return line[1:].strip()
    return None


def tokenize_lean_tactic(tactic: str) -> List[str]:
    """
    Токенизирует Lean тактику.
    
    Args:
        tactic: Строка тактики
        
    Returns:
        Список токенов
    """
    variable_pattern = VARIABLE_PATTERN
    operator_pattern = r'[:=<>∈∉≤≥+\-*/^∀∃¬⁻¹↔∧∨]+'
    punctuation_pattern = r'[,⟨⟩\[\](){}|·]'
    comment_pattern = r'--.*'
    
    # Удаляем комментарии
    tactic = re.sub(comment_pattern, '', tactic)
    
    tokens = []
    while tactic:
        # Пробелы
        if tactic[0].isspace():
            tactic = tactic[1:]
            continue
        
        # Переменные/идентификаторы
        match = re.match(variable_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        
        # Операторы
        match = re.match(operator_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        
        # Пунктуация
        match = re.match(punctuation_pattern, tactic)
        if match:
            tokens.append(match.group())
            tactic = tactic[match.end():]
            continue
        
        # Остальные символы
        tokens.append(tactic[0])
        tactic = tactic[1:]
    
    return tokens


def state_complexity(state: str) -> int:
    """
    Вычисляет сложность состояния (для приоритета в BFS).
    
    Args:
        state: Pretty-printed состояние
        
    Returns:
        Числовая сложность
    """
    complexity = 0
    n_goals = 0
    
    for line in state.strip().split('\n'):
        line = line.strip()
        if line.startswith('⊢'):
            goal = line[1:].strip()
            complexity = max(complexity, len(goal))
            n_goals += 1
    
    # Штраф за False (обычно недоказуемо)
    if '⊢ False' in state:
        complexity += 100000
    
    return complexity + n_goals - 1


class PriorityQueue:
    """Очередь с приоритетом для BFS."""
    
    def __init__(self):
        self._queue = []
        self._index = 0
    
    def size(self) -> int:
        return len(self._queue)
    
    def push(self, item: Any, priority: int):
        """Добавляет элемент с приоритетом (меньше = выше приоритет)."""
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1
    
    def pop(self) -> Optional[Any]:
        """Извлекает элемент с наивысшим приоритетом."""
        if not self._queue:
            return None
        return heapq.heappop(self._queue)[2]
    
    def __bool__(self) -> bool:
        return len(self._queue) > 0
