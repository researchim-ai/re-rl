# re_rl/tasks/formal/theorem_templates.py
"""
Шаблоны теорем и доказательств для Lean 4.

Каждый шаблон содержит:
- theorem: формулировка теоремы
- proof: доказательство (тактики)
- natural_statement: формулировка на естественном языке (ru/en)
- natural_proof: объяснение доказательства на естественном языке
- difficulty: базовая сложность (1-10)
- tags: теги для фильтрации
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'theorem_templates_i18n.json')


from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random


@dataclass
class TheoremTemplate:
    """Шаблон теоремы с доказательством."""
    
    name: str
    theorem: str  # Lean 4 формулировка
    proof: str    # Lean 4 тактики
    natural_statement: Dict[str, str]  # {lang: описание}
    natural_proof: Dict[str, str]      # {lang: объяснение}
    difficulty: int = 1
    category: str = "propositional"
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, List[Any]] = field(default_factory=dict)  # Для вариаций
    
    def instantiate(self, **kwargs) -> "TheoremTemplate":
        """Создаёт конкретный экземпляр шаблона с подставленными параметрами."""
        theorem = self.theorem.format(**kwargs) if kwargs else self.theorem
        proof = self.proof.format(**kwargs) if kwargs else self.proof
        name = self.name.format(**kwargs) if kwargs else self.name
        
        natural_statement = {
            lang: stmt.format(**kwargs) if kwargs else stmt 
            for lang, stmt in self.natural_statement.items()
        }
        natural_proof = {
            lang: prf.format(**kwargs) if kwargs else prf
            for lang, prf in self.natural_proof.items()
        }
        
        return TheoremTemplate(
            name=name,
            theorem=theorem,
            proof=proof,
            natural_statement=natural_statement,
            natural_proof=natural_proof,
            difficulty=self.difficulty,
            category=self.category,
            tags=self.tags.copy(),
            parameters={},  # Уже инстанциирован
        )
    
    def get_random_instance(self) -> "TheoremTemplate":
        """Создаёт случайный экземпляр из параметров."""
        if not self.parameters:
            return self
        
        kwargs = {
            key: random.choice(values) 
            for key, values in self.parameters.items()
        }
        return self.instantiate(**kwargs)


# =============================================================================
# ПРОПОЗИЦИОНАЛЬНАЯ ЛОГИКА (difficulty 1-3)
# =============================================================================

PROPOSITIONAL_TEMPLATES = [
    # Тождество
    TheoremTemplate(
        name="identity",
        theorem="theorem identity : ∀ (p : Prop), p → p := by",
        proof="intro p hp\nexact hp",
        natural_statement={
            "ru": texts.literal('literals.s0'),
            "en": "Prove that for any proposition p: if p is true, then p is true.",
        },
        natural_proof={
            "ru": texts.literal('literals.s1'),
            "en": "Step 1: Introduce arbitrary proposition p and assumption hp: p.\n"
                  "Step 2: Goal is to prove p. Use hp directly.",
        },
        difficulty=1,
        category="propositional",
        tags=["basic", "implication"],
    ),
    
    # Коммутативность конъюнкции
    TheoremTemplate(
        name="and_comm",
        theorem="theorem and_comm : ∀ (p q : Prop), p ∧ q → q ∧ p := by",
        proof="intro p q h\nexact ⟨h.2, h.1⟩",
        natural_statement={
            "ru": texts.literal('literals.s2'),
            "en": "Prove that conjunction is commutative: p ∧ q → q ∧ p.",
        },
        natural_proof={
            "ru": texts.literal('literals.s3'),
            "en": "Step 1: Let h be a proof of p ∧ q.\n"
                  "Step 2: Extract h.1 : p and h.2 : q from h.\n"
                  "Step 3: Construct pair ⟨h.2, h.1⟩ : q ∧ p.",
        },
        difficulty=2,
        category="propositional",
        tags=["conjunction", "commutativity"],
    ),
    
    # Коммутативность дизъюнкции
    TheoremTemplate(
        name="or_comm",
        theorem="theorem or_comm : ∀ (p q : Prop), p ∨ q → q ∨ p := by",
        proof="intro p q h\ncases h with\n| inl hp => exact Or.inr hp\n| inr hq => exact Or.inl hq",
        natural_statement={
            "ru": texts.literal('literals.s4'),
            "en": "Prove that disjunction is commutative: p ∨ q → q ∨ p.",
        },
        natural_proof={
            "ru": texts.literal('literals.s5'),
            "en": "Step 1: Let h be a proof of p ∨ q.\n"
                  "Step 2: Case analysis:\n"
                  "  - If p is true (hp), then q ∨ p holds by Or.inr hp.\n"
                  "  - If q is true (hq), then q ∨ p holds by Or.inl hq.",
        },
        difficulty=3,
        category="propositional",
        tags=["disjunction", "commutativity"],
    ),
    
    # Импликация транзитивна
    TheoremTemplate(
        name="impl_trans",
        theorem="theorem impl_trans : ∀ (p q r : Prop), (p → q) → (q → r) → (p → r) := by",
        proof="intro p q r hpq hqr hp\nexact hqr (hpq hp)",
        natural_statement={
            "ru": texts.literal('literals.s6'),
            "en": "Prove transitivity of implication: (p → q) → (q → r) → (p → r).",
        },
        natural_proof={
            "ru": texts.literal('literals.s7'),
            "en": "Step 1: Introduce assumptions hpq: p → q, hqr: q → r, hp: p.\n"
                  "Step 2: Apply hpq to hp to get q.\n"
                  "Step 3: Apply hqr to q to get r.",
        },
        difficulty=2,
        category="propositional",
        tags=["implication", "transitivity"],
    ),
    
    # Modus ponens
    TheoremTemplate(
        name="modus_ponens",
        theorem="theorem modus_ponens : ∀ (p q : Prop), p → (p → q) → q := by",
        proof="intro p q hp hpq\nexact hpq hp",
        natural_statement={
            "ru": texts.literal('literals.s8'),
            "en": "Prove modus ponens: p → (p → q) → q.",
        },
        natural_proof={
            "ru": texts.literal('literals.s9'),
            "en": "Step 1: Introduce hp: p and hpq: p → q.\n"
                  "Step 2: Apply hpq to hp to get q.",
        },
        difficulty=1,
        category="propositional",
        tags=["modus_ponens", "basic"],
    ),
    
    # Ассоциативность конъюнкции
    TheoremTemplate(
        name="and_assoc",
        theorem="theorem and_assoc : ∀ (p q r : Prop), (p ∧ q) ∧ r ↔ p ∧ (q ∧ r) := by",
        proof="intro p q r\nconstructor\n· intro h\n  exact ⟨h.1.1, h.1.2, h.2⟩\n· intro h\n  exact ⟨⟨h.1, h.2.1⟩, h.2.2⟩",
        natural_statement={
            "ru": texts.literal('literals.s10'),
            "en": "Prove associativity of conjunction: (p ∧ q) ∧ r ↔ p ∧ (q ∧ r).",
        },
        natural_proof={
            "ru": texts.literal('literals.s11'),
            "en": "Prove both directions:\n"
                  "→: From ((p ∧ q) ∧ r) extract p, q, r and construct (p ∧ (q ∧ r)).\n"
                  "←: From (p ∧ (q ∧ r)) extract p, q, r and construct ((p ∧ q) ∧ r).",
        },
        difficulty=3,
        category="propositional",
        tags=["conjunction", "associativity", "iff"],
    ),
    
    # Контрапозиция
    TheoremTemplate(
        name="contrapositive",
        theorem="theorem contrapositive : ∀ (p q : Prop), (p → q) → (¬q → ¬p) := by",
        proof="intro p q hpq hnq hp\nexact hnq (hpq hp)",
        natural_statement={
            "ru": texts.literal('literals.s12'),
            "en": "Prove contrapositive: (p → q) → (¬q → ¬p).",
        },
        natural_proof={
            "ru": texts.literal('literals.s13'),
            "en": "Step 1: Let hpq: p → q, hnq: ¬q, hp: p.\n"
                  "Step 2: From hp and hpq we get q.\n"
                  "Step 3: But hnq: ¬q — contradiction.",
        },
        difficulty=3,
        category="propositional",
        tags=["negation", "contrapositive"],
    ),
]


# =============================================================================
# АРИФМЕТИКА НАТУРАЛЬНЫХ ЧИСЕЛ (difficulty 3-6)
# =============================================================================

NAT_ARITHMETIC_TEMPLATES = [
    # n + 0 = n
    TheoremTemplate(
        name="add_zero",
        theorem="theorem add_zero : ∀ (n : Nat), n + 0 = n := by",
        proof="intro n\nrfl",
        natural_statement={
            "ru": texts.literal('literals.s14'),
            "en": "Prove that n + 0 = n for any natural number n.",
        },
        natural_proof={
            "ru": texts.literal('literals.s15'),
            "en": "Step 1: By definition of addition in Nat, n + 0 computes to n.\n"
                  "Step 2: This holds by reflexivity (rfl).",
        },
        difficulty=3,
        category="nat_arithmetic",
        tags=["addition", "zero", "basic"],
    ),
    
    # 0 + n = n (требует индукции)
    TheoremTemplate(
        name="zero_add",
        theorem="theorem zero_add : ∀ (n : Nat), 0 + n = n := by",
        proof="intro n\ninduction n with\n| zero => rfl\n| succ n ih => simp [Nat.add_succ, ih]",
        natural_statement={
            "ru": texts.literal('literals.s16'),
            "en": "Prove that 0 + n = n for any natural number n.",
        },
        natural_proof={
            "ru": texts.literal('literals.s17'),
            "en": "Proof by induction:\n"
                  "Base: 0 + 0 = 0 — holds by rfl.\n"
                  "Step: Assume 0 + n = n (IH). Then 0 + (n+1) = (0 + n) + 1 = n + 1.",
        },
        difficulty=4,
        category="nat_arithmetic",
        tags=["addition", "zero", "induction"],
    ),
    
    # Коммутативность сложения
    TheoremTemplate(
        name="add_comm",
        theorem="theorem add_comm' : ∀ (n m : Nat), n + m = m + n := by",
        proof="intro n m\ninduction n with\n| zero => simp [Nat.zero_add, Nat.add_zero]\n| succ n ih => simp [Nat.succ_add, Nat.add_succ, ih]",
        natural_statement={
            "ru": texts.literal('literals.s18'),
            "en": "Prove commutativity of addition: n + m = m + n.",
        },
        natural_proof={
            "ru": texts.literal('literals.s19'),
            "en": "Proof by induction on n:\n"
                  "Base: 0 + m = m = m + 0.\n"
                  "Step: (n+1) + m = (n + m) + 1 = (m + n) + 1 = m + (n+1).",
        },
        difficulty=5,
        category="nat_arithmetic",
        tags=["addition", "commutativity", "induction"],
    ),
    
    # n * 0 = 0
    TheoremTemplate(
        name="mul_zero",
        theorem="theorem mul_zero : ∀ (n : Nat), n * 0 = 0 := by",
        proof="intro n\nrfl",
        natural_statement={
            "ru": texts.literal('literals.s20'),
            "en": "Prove that n * 0 = 0 for any natural number n.",
        },
        natural_proof={
            "ru": texts.literal('literals.s21'),
            "en": "By definition of multiplication in Nat, n * 0 = 0.",
        },
        difficulty=3,
        category="nat_arithmetic",
        tags=["multiplication", "zero", "basic"],
    ),
    
    # n * 1 = n
    TheoremTemplate(
        name="mul_one",
        theorem="theorem mul_one : ∀ (n : Nat), n * 1 = n := by",
        proof="intro n\nsimp [Nat.mul_one]",
        natural_statement={
            "ru": texts.literal('literals.s22'),
            "en": "Prove that n * 1 = n for any natural number n.",
        },
        natural_proof={
            "ru": "n * 1 = n * (0 + 1) = n * 0 + n = 0 + n = n.",
            "en": "n * 1 = n * (0 + 1) = n * 0 + n = 0 + n = n.",
        },
        difficulty=4,
        category="nat_arithmetic",
        tags=["multiplication", "one"],
    ),
    
    # Дистрибутивность (упрощённая)
    TheoremTemplate(
        name="mul_add_simple",
        theorem="theorem mul_two : ∀ (n : Nat), n * 2 = n + n := by",
        proof="intro n\nsimp [Nat.mul_succ, Nat.mul_one]",
        natural_statement={
            "ru": texts.literal('literals.s23'),
            "en": "Prove that n * 2 = n + n.",
        },
        natural_proof={
            "ru": "n * 2 = n * (1 + 1) = n * 1 + n * 1 = n + n.",
            "en": "n * 2 = n * (1 + 1) = n * 1 + n * 1 = n + n.",
        },
        difficulty=4,
        category="nat_arithmetic",
        tags=["multiplication", "distributivity"],
    ),
    
    # Ассоциативность сложения
    TheoremTemplate(
        name="add_assoc",
        theorem="theorem add_assoc' : ∀ (a b c : Nat), (a + b) + c = a + (b + c) := by",
        proof="intro a b c\ninduction c with\n| zero => rfl\n| succ c ih => simp [Nat.add_succ, ih]",
        natural_statement={
            "ru": texts.literal('literals.s24'),
            "en": "Prove associativity of addition: (a + b) + c = a + (b + c).",
        },
        natural_proof={
            "ru": texts.literal('literals.s25'),
            "en": "Proof by induction on c:\n"
                  "Base: (a + b) + 0 = a + b = a + (b + 0).\n"
                  "Step: (a + b) + (c+1) = ((a + b) + c) + 1 = (a + (b + c)) + 1 = a + (b + (c+1)).",
        },
        difficulty=5,
        category="nat_arithmetic",
        tags=["addition", "associativity", "induction"],
    ),
]


# =============================================================================
# ПРЕДИКАТНАЯ ЛОГИКА (difficulty 2-4)
# =============================================================================

PREDICATE_TEMPLATES = [
    # ∀ elim
    TheoremTemplate(
        name="forall_elim",
        theorem="theorem forall_elim : ∀ (P : α → Prop) (a : α), (∀ x, P x) → P a := by",
        proof="intro P a h\nexact h a",
        natural_statement={
            "ru": texts.literal('literals.s26'),
            "en": "Prove universal elimination: (∀ x, P x) → P a.",
        },
        natural_proof={
            "ru": texts.literal('literals.s27'),
            "en": "If P holds for all x, then in particular P holds for a.",
        },
        difficulty=2,
        category="predicate",
        tags=["forall", "elimination"],
    ),
    
    # ∃ intro
    TheoremTemplate(
        name="exists_intro",
        theorem="theorem exists_intro : ∀ (P : α → Prop) (a : α), P a → ∃ x, P x := by",
        proof="intro P a h\nexact ⟨a, h⟩",
        natural_statement={
            "ru": texts.literal('literals.s28'),
            "en": "Prove existential introduction: P a → ∃ x, P x.",
        },
        natural_proof={
            "ru": texts.literal('literals.s29'),
            "en": "If P a is true, then there exists x (namely a) for which P x.",
        },
        difficulty=2,
        category="predicate",
        tags=["exists", "introduction"],
    ),
    
    # ∀ распределяется по ∧
    TheoremTemplate(
        name="forall_and_distrib",
        theorem="theorem forall_and_distrib : ∀ (P Q : α → Prop), (∀ x, P x ∧ Q x) → (∀ x, P x) ∧ (∀ x, Q x) := by",
        proof="intro P Q h\nconstructor\n· intro x; exact (h x).1\n· intro x; exact (h x).2",
        natural_statement={
            "ru": texts.literal('literals.s30'),
            "en": "Prove that ∀ distributes over ∧: (∀ x, P x ∧ Q x) → (∀ x, P x) ∧ (∀ x, Q x).",
        },
        natural_proof={
            "ru": texts.literal('literals.s31'),
            "en": "From h: ∀ x, P x ∧ Q x, for any x we get P x (via h(x).1) and Q x (via h(x).2).",
        },
        difficulty=3,
        category="predicate",
        tags=["forall", "conjunction", "distributivity"],
    ),
    
    # ∃ и ∨
    TheoremTemplate(
        name="exists_or",
        theorem="theorem exists_or : ∀ (P Q : α → Prop), (∃ x, P x ∨ Q x) → (∃ x, P x) ∨ (∃ x, Q x) := by",
        proof="intro P Q ⟨x, h⟩\ncases h with\n| inl hp => exact Or.inl ⟨x, hp⟩\n| inr hq => exact Or.inr ⟨x, hq⟩",
        natural_statement={
            "ru": texts.literal('literals.s32'),
            "en": "Prove: (∃ x, P x ∨ Q x) → (∃ x, P x) ∨ (∃ x, Q x).",
        },
        natural_proof={
            "ru": texts.literal('literals.s33'),
            "en": "Suppose there exists x such that P x ∨ Q x.\n"
                  "If P x, then ∃ x, P x.\n"
                  "If Q x, then ∃ x, Q x.",
        },
        difficulty=4,
        category="predicate",
        tags=["exists", "disjunction"],
    ),
]


# =============================================================================
# РАВЕНСТВО И ОТНОШЕНИЯ (difficulty 2-4)
# =============================================================================

EQUALITY_TEMPLATES = [
    # Симметричность
    TheoremTemplate(
        name="eq_symm",
        theorem="theorem eq_symm' : ∀ (a b : α), a = b → b = a := by",
        proof="intro a b h\nexact h.symm",
        natural_statement={
            "ru": texts.literal('literals.s34'),
            "en": "Prove symmetry of equality: a = b → b = a.",
        },
        natural_proof={
            "ru": texts.literal('literals.s35'),
            "en": "If a = b, then by symmetry of equality b = a.",
        },
        difficulty=2,
        category="equality",
        tags=["equality", "symmetry"],
    ),
    
    # Транзитивность
    TheoremTemplate(
        name="eq_trans",
        theorem="theorem eq_trans' : ∀ (a b c : α), a = b → b = c → a = c := by",
        proof="intro a b c hab hbc\nexact hab.trans hbc",
        natural_statement={
            "ru": texts.literal('literals.s36'),
            "en": "Prove transitivity of equality: a = b → b = c → a = c.",
        },
        natural_proof={
            "ru": texts.literal('literals.s37'),
            "en": "If a = b and b = c, then a = c by transitivity.",
        },
        difficulty=2,
        category="equality",
        tags=["equality", "transitivity"],
    ),
    
    # Подстановка
    TheoremTemplate(
        name="eq_subst",
        theorem="theorem eq_subst : ∀ (P : α → Prop) (a b : α), a = b → P a → P b := by",
        proof="intro P a b h ha\nexact h ▸ ha",
        natural_statement={
            "ru": texts.literal('literals.s38'),
            "en": "Prove substitution principle: a = b → P a → P b.",
        },
        natural_proof={
            "ru": texts.literal('literals.s39'),
            "en": "If a = b and P a, then substituting b for a we get P b.",
        },
        difficulty=3,
        category="equality",
        tags=["equality", "substitution"],
    ),
]


# =============================================================================
# СПИСКИ (difficulty 4-6)
# =============================================================================

LIST_TEMPLATES = [
    # Длина пустого списка
    TheoremTemplate(
        name="length_nil",
        theorem="theorem length_nil : ([] : List α).length = 0 := by",
        proof="rfl",
        natural_statement={
            "ru": texts.literal('literals.s40'),
            "en": "Prove that the length of an empty list is 0.",
        },
        natural_proof={
            "ru": texts.literal('literals.s41'),
            "en": "By definition of length, [].length = 0.",
        },
        difficulty=3,
        category="list",
        tags=["list", "length", "basic"],
    ),
    
    # Длина cons
    TheoremTemplate(
        name="length_cons",
        theorem="theorem length_cons : ∀ (a : α) (l : List α), (a :: l).length = l.length + 1 := by",
        proof="intro a l\nrfl",
        natural_statement={
            "ru": texts.literal('literals.s42'),
            "en": "Prove that length (a :: l) = length l + 1.",
        },
        natural_proof={
            "ru": texts.literal('literals.s43'),
            "en": "By definition of length for cons.",
        },
        difficulty=3,
        category="list",
        tags=["list", "length", "cons"],
    ),
    
    # Append nil
    TheoremTemplate(
        name="append_nil",
        theorem="theorem append_nil : ∀ (l : List α), l ++ [] = l := by",
        proof="intro l\ninduction l with\n| nil => rfl\n| cons a l ih => simp [List.cons_append, ih]",
        natural_statement={
            "ru": texts.literal('literals.s44'),
            "en": "Prove that l ++ [] = l for any list l.",
        },
        natural_proof={
            "ru": texts.literal('literals.s45'),
            "en": "By induction on l:\n"
                  "Base: [] ++ [] = [].\n"
                  "Step: (a :: l) ++ [] = a :: (l ++ []) = a :: l.",
        },
        difficulty=4,
        category="list",
        tags=["list", "append", "induction"],
    ),
    
    # Nil append
    TheoremTemplate(
        name="nil_append",
        theorem="theorem nil_append : ∀ (l : List α), [] ++ l = l := by",
        proof="intro l\nrfl",
        natural_statement={
            "ru": texts.literal('literals.s46'),
            "en": "Prove that [] ++ l = l for any list l.",
        },
        natural_proof={
            "ru": texts.literal('literals.s47'),
            "en": "By definition of append, [] ++ l = l.",
        },
        difficulty=3,
        category="list",
        tags=["list", "append", "basic"],
    ),
    
    # Reverse reverse
    TheoremTemplate(
        name="reverse_reverse",
        theorem="theorem reverse_reverse : ∀ (l : List α), l.reverse.reverse = l := by",
        proof="intro l\nsimp",
        natural_statement={
            "ru": texts.literal('literals.s48'),
            "en": "Prove that reverse (reverse l) = l.",
        },
        natural_proof={
            "ru": texts.literal('literals.s49'),
            "en": "Reversing a list twice returns the original list.",
        },
        difficulty=5,
        category="list",
        tags=["list", "reverse"],
    ),
]


# =============================================================================
# ОБЪЕДИНЁННЫЙ СЛОВАРЬ ШАБЛОНОВ
# =============================================================================

THEOREM_TEMPLATES: Dict[str, List[TheoremTemplate]] = {
    "propositional": PROPOSITIONAL_TEMPLATES,
    "nat_arithmetic": NAT_ARITHMETIC_TEMPLATES,
    "predicate": PREDICATE_TEMPLATES,
    "equality": EQUALITY_TEMPLATES,
    "list": LIST_TEMPLATES,
}


def get_theorem_categories() -> List[str]:
    """Возвращает список всех категорий теорем."""
    return list(THEOREM_TEMPLATES.keys())


def get_templates_by_difficulty(min_diff: int = 1, max_diff: int = 10) -> List[TheoremTemplate]:
    """Возвращает шаблоны в заданном диапазоне сложности."""
    result = []
    for templates in THEOREM_TEMPLATES.values():
        for t in templates:
            if min_diff <= t.difficulty <= max_diff:
                result.append(t)
    return result


def get_random_template(
    category: Optional[str] = None,
    min_difficulty: int = 1,
    max_difficulty: int = 10,
) -> TheoremTemplate:
    """Возвращает случайный шаблон теоремы."""
    if category and category in THEOREM_TEMPLATES:
        templates = [
            t for t in THEOREM_TEMPLATES[category]
            if min_difficulty <= t.difficulty <= max_difficulty
        ]
    else:
        templates = get_templates_by_difficulty(min_difficulty, max_difficulty)
    
    if not templates:
        raise ValueError(f"No templates found for category={category}, difficulty={min_difficulty}-{max_difficulty}")
    
    return random.choice(templates)
