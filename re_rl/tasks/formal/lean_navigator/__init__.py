# re_rl/tasks/formal/lean_navigator/__init__.py
"""
LeanNavigator — воспроизведение статьи
"Generating Millions of Lean Theorems with Proofs by Exploring State Transition Graphs"

Подход:
1. Извлечение шаблонов тактик из traced Mathlib (.ast.json)
2. FAISS RAG для поиска релевантных тактик по состоянию
3. BFS exploration через Pantograph (per-file server)
4. Обучение BERT-based retriever (triplet loss)

Использование:
    from re_rl.tasks.formal.lean_navigator import (
        PantographDojo, LeanNavigatorExplorer, TacticRAG,
        run_lean_navigator, load_theorems_from_env,
    )
"""

# === Core: BFS + Pantograph + RAG ===
from re_rl.tasks.formal.lean_navigator.core import (
    TacticTemplateExtractor,
    TacticRAG,
    PantographDojo,
    LeanNavigatorExplorer,
    run_lean_navigator,
    NavigatorResult,
    TracedTheorem,
    TrainingPair,
    ProofState,
    ProofFinished,
    PriorityQueue,
    load_theorems_from_ast_dir,
    load_theorems_from_env,
    classify_lean_elements,
    explore_state_complexity,
    generate_tactics_from_template,
    get_inverse_tactic,
)

# === RAG Trainer (BERT retriever) ===
from re_rl.tasks.formal.lean_navigator.rag_trainer import (
    TacticTripletDataset,
    TripletLoss,
    TripletDataGenerator,
    TacticBERTTrainer,
    TrainedTacticRAG,
    train_tactic_rag,
)

# === State Explorer (old BFS) ===
from re_rl.tasks.formal.lean_navigator.state_explorer import (
    StateExplorer,
    StateNode,
    ExplorationResult,
    ExplorationStats,
    explore_theorem,
)

# === Dataset Generator ===
from re_rl.tasks.formal.lean_navigator.dataset_generator import (
    LeanDatasetGenerator,
    DatasetConfig,
    DatasetStats,
    generate_lean_dataset,
)

# === Lean Utils ===
from re_rl.tasks.formal.lean_navigator.lean_utils import (
    extract_hypotheses,
    extract_variables,
    extract_goal,
    state_complexity,
    tokenize_lean_tactic,
    LEAN4_TACTICS,
)

# === ML Tactic Generator ===
from re_rl.tasks.formal.lean_navigator.ml_tactic_generator import (
    MLTacticGenerator,
    HFTacticGenerator,
    ExternalAPITacticGenerator,
    LeanDojoProverGenerator,
    EmbeddingTacticRetriever,
    HybridTacticGenerator,
    create_ml_generator,
)

__all__ = [
    # Core
    "TacticTemplateExtractor", "TacticRAG", "PantographDojo",
    "LeanNavigatorExplorer", "run_lean_navigator", "NavigatorResult",
    "TracedTheorem", "TrainingPair", "ProofState", "ProofFinished",
    "PriorityQueue", "load_theorems_from_ast_dir", "load_theorems_from_env",
    "classify_lean_elements", "explore_state_complexity",
    "generate_tactics_from_template", "get_inverse_tactic",
    # RAG Trainer
    "TacticTripletDataset", "TripletLoss", "TripletDataGenerator",
    "TacticBERTTrainer", "TrainedTacticRAG", "train_tactic_rag",
    # State Explorer
    "StateExplorer", "StateNode", "ExplorationResult",
    "ExplorationStats", "explore_theorem",
    # Dataset Generator
    "LeanDatasetGenerator", "DatasetConfig", "DatasetStats",
    "generate_lean_dataset",
    # Lean Utils
    "extract_hypotheses", "extract_variables", "extract_goal",
    "state_complexity", "tokenize_lean_tactic", "LEAN4_TACTICS",
    # ML Tactic Generator
    "MLTacticGenerator", "HFTacticGenerator", "ExternalAPITacticGenerator",
    "LeanDojoProverGenerator", "EmbeddingTacticRetriever",
    "HybridTacticGenerator", "create_ml_generator",
]
