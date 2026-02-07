# re_rl/tasks/formal/__init__.py
"""
Formal mathematics tasks - генерация теорем и доказательств в Lean 4.

Модуль включает:

1. **Шаблонная генерация** (без зависимостей):
   - LeanProofTask — задачи на доказательство из шаблонов
   - THEOREM_TEMPLATES — 24+ предопределённых теорем

2. **LeanNavigator** (BFS через Pantograph):
   - LeanNavigatorExplorer — BFS исследование графа переходов
   - TacticRAG — FAISS retrieval тактик
   - PantographDojo — обёртка над Pantograph Server
   - TacticBERTTrainer — обучение BERT retriever

3. Будущие подходы добавляются как поддиректории tasks/formal/<approach>/

Пример шаблонной генерации:
    >>> from re_rl.tasks.formal import LeanProofTask
    >>> task = LeanProofTask.from_difficulty(difficulty=3, language="ru")
    >>> task.solve()
    >>> print(task.to_sft_format())

Пример LeanNavigator:
    >>> from re_rl.tasks.formal.lean_navigator import (
    ...     PantographDojo, LeanNavigatorExplorer, run_lean_navigator,
    ... )
"""

# === Шаблонная генерация (работает без зависимостей) ===
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

# === Генерация тактик (без ML) ===
from re_rl.tasks.formal.tactic_generator import (
    TacticGenerator,
    TacticTemplate as TacticTemplateGen,
    TACTIC_TEMPLATES,
    GOAL_PATTERN_TACTICS,
    generate_tactics,
    generate_tactics_for_goal,
)

# === Утилиты установки ===
from re_rl.tasks.formal.setup_lean_repos import (
    REPOS as LEAN_REPOS,
    add_custom_mathlib4,
    trace_repo,
    list_cached_repos,
    check_elan_installed,
    _apply_extractor_fix,
)

# === LeanNavigator (lazy import — тяжёлые зависимости) ===
# Прямые импорты для обратной совместимости:
# from re_rl.tasks.formal import PantographDojo, TacticRAG, etc.
try:
    from re_rl.tasks.formal.lean_navigator import (
        # Core
        TacticTemplateExtractor,
        TacticRAG,
        PantographDojo,
        LeanNavigatorExplorer,
        run_lean_navigator,
        NavigatorResult,
        TracedTheorem,
        load_theorems_from_ast_dir,
        load_theorems_from_env,
        # Lean Utils
        ProofState,
        PriorityQueue,
        extract_hypotheses,
        extract_variables,
        extract_goal,
        classify_lean_elements,
        state_complexity,
        tokenize_lean_tactic,
        LEAN4_TACTICS,
        # State Explorer
        StateExplorer,
        StateNode,
        TrainingPair,
        ExplorationResult,
        ExplorationStats,
        explore_theorem,
        # Dataset Generator
        LeanDatasetGenerator,
        DatasetConfig,
        DatasetStats,
        generate_lean_dataset,
        # ML Tactic Generator
        MLTacticGenerator,
        HFTacticGenerator,
        ExternalAPITacticGenerator,
        LeanDojoProverGenerator,
        EmbeddingTacticRetriever,
        HybridTacticGenerator,
        create_ml_generator,
        # RAG Trainer
        TacticTripletDataset,
        TripletLoss,
        TripletDataGenerator,
        TacticBERTTrainer,
        TrainedTacticRAG,
        train_tactic_rag,
    )
except ImportError:
    pass  # Тяжёлые зависимости не установлены — это нормально

__all__ = [
    # Шаблонная генерация
    "LeanProofTask",
    "generate_lean_proof_task",
    "generate_lean_proof_batch",
    "TheoremTemplate",
    "THEOREM_TEMPLATES",
    "get_theorem_categories",
    "get_random_template",
    
    # Генерация тактик
    "TacticGenerator",
    "TacticTemplateGen",
    "TACTIC_TEMPLATES",
    "GOAL_PATTERN_TACTICS",
    "generate_tactics",
    "generate_tactics_for_goal",
    
    # Утилиты установки
    "LEAN_REPOS",
    "add_custom_mathlib4",
    "trace_repo",
    "list_cached_repos",
    "check_elan_installed",
    "_apply_extractor_fix",
    
    # LeanNavigator (доступны если установлены зависимости)
    "TacticTemplateExtractor", "TacticRAG", "PantographDojo",
    "LeanNavigatorExplorer", "run_lean_navigator", "NavigatorResult",
    "TracedTheorem", "load_theorems_from_ast_dir", "load_theorems_from_env",
    "ProofState", "PriorityQueue", "extract_hypotheses", "extract_variables",
    "extract_goal", "classify_lean_elements", "state_complexity",
    "tokenize_lean_tactic", "LEAN4_TACTICS",
    "StateExplorer", "StateNode", "TrainingPair",
    "ExplorationResult", "ExplorationStats", "explore_theorem",
    "LeanDatasetGenerator", "DatasetConfig", "DatasetStats",
    "generate_lean_dataset",
    "MLTacticGenerator", "HFTacticGenerator", "ExternalAPITacticGenerator",
    "LeanDojoProverGenerator", "EmbeddingTacticRetriever",
    "HybridTacticGenerator", "create_ml_generator",
    "TacticTripletDataset", "TripletLoss", "TripletDataGenerator",
    "TacticBERTTrainer", "TrainedTacticRAG", "train_tactic_rag",
]
