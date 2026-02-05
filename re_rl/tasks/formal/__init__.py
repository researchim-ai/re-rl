# re_rl/tasks/formal/__init__.py
"""
Formal mathematics tasks - генерация теорем и доказательств в Lean 4.

Модуль включает:

1. **Шаблонная генерация** (без LeanDojo):
   - LeanProofTask — задачи на доказательство из шаблонов
   - THEOREM_TEMPLATES — 24+ предопределённых теорем

2. **Генерация через BFS** (требует LeanDojo):
   - StateExplorer — исследование графа состояний
   - TacticGenerator — генерация тактик без ML
   - LeanDatasetGenerator — сбор датасетов для обучения

Пример шаблонной генерации:
    >>> from re_rl.tasks.formal import LeanProofTask
    >>> task = LeanProofTask.from_difficulty(difficulty=3, language="ru")
    >>> task.solve()
    >>> print(task.to_sft_format())

Пример генерации датасета (требует LeanDojo):
    >>> from re_rl.tasks.formal import generate_lean_dataset
    >>> stats = generate_lean_dataset(
    ...     repo_url="https://github.com/leanprover-community/mathlib4",
    ...     commit="abc123",
    ...     output_dir="./my_dataset",
    ...     max_theorems=100,
    ... )
"""

# === Шаблонная генерация (работает без LeanDojo) ===
from re_rl.tasks.formal.lean_proof_task import (
    LeanProofTask,
    generate_lean_proof_task,
    generate_lean_proof_batch,
)
from re_rl.tasks.formal.theorem_templates import (
    TheoremTemplate,
    THEOREM_TEMPLATES,
    get_theorem_categories,
    get_random_template,
)

# === Утилиты для работы с Lean ===
from re_rl.tasks.formal.lean_utils import (
    ProofState,
    PriorityQueue,
    extract_hypotheses,
    extract_variables,
    extract_goal,
    classify_lean_elements,
    state_complexity,
    tokenize_lean_tactic,
    LEAN4_TACTICS,
)

# === Генерация тактик (без ML) ===
from re_rl.tasks.formal.tactic_generator import (
    TacticGenerator,
    TacticTemplate as TacticTemplateGen,
    TACTIC_TEMPLATES,
    GOAL_PATTERN_TACTICS,
    generate_tactics,
    generate_tactics_for_goal,
)

# === BFS исследование и генерация датасетов ===
from re_rl.tasks.formal.state_explorer import (
    StateExplorer,
    StateNode,
    TrainingPair,
    ExplorationResult,
    ExplorationStats,
    explore_theorem,
)
from re_rl.tasks.formal.dataset_generator import (
    LeanDatasetGenerator,
    DatasetConfig,
    DatasetStats,
    generate_lean_dataset,
)

# === ML-ускоренная генерация тактик ===
from re_rl.tasks.formal.ml_tactic_generator import (
    MLTacticGenerator,
    HFTacticGenerator,
    ExternalAPITacticGenerator,
    LeanDojoProverGenerator,
    EmbeddingTacticRetriever,
    HybridTacticGenerator,
    create_ml_generator,
)

__all__ = [
    # Шаблонная генерация
    "LeanProofTask",
    "generate_lean_proof_task",
    "generate_lean_proof_batch",
    "TheoremTemplate",
    "THEOREM_TEMPLATES",
    "get_theorem_categories",
    "get_random_template",
    
    # Утилиты
    "ProofState",
    "PriorityQueue",
    "extract_hypotheses",
    "extract_variables",
    "extract_goal",
    "classify_lean_elements",
    "state_complexity",
    "tokenize_lean_tactic",
    "LEAN4_TACTICS",
    
    # Генерация тактик
    "TacticGenerator",
    "TacticTemplateGen",
    "TACTIC_TEMPLATES",
    "GOAL_PATTERN_TACTICS",
    "generate_tactics",
    "generate_tactics_for_goal",
    
    # BFS исследование
    "StateExplorer",
    "StateNode",
    "TrainingPair",
    "ExplorationResult",
    "ExplorationStats",
    "explore_theorem",
    
    # Генерация датасетов
    "LeanDatasetGenerator",
    "DatasetConfig",
    "DatasetStats",
    "generate_lean_dataset",
    
    # ML генераторы тактик
    "MLTacticGenerator",
    "HFTacticGenerator",
    "ExternalAPITacticGenerator",
    "LeanDojoProverGenerator",
    "EmbeddingTacticRetriever",
    "HybridTacticGenerator",
    "create_ml_generator",
]
