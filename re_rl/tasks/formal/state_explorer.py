# re_rl/tasks/formal/state_explorer.py
"""
BFS исследование графа переходов состояний Lean.

Реализует алгоритм из LeanNavigator:
1. Начинаем с начального состояния теоремы
2. Применяем тактики и получаем новые состояния
3. Исследуем граф в ширину до ProofFinished
4. Собираем все пары (state, tactic) как обучающие данные

Требует: LeanDojo для взаимодействия с Lean
"""

import time
import random
from typing import List, Dict, Tuple, Optional, Any, Set, Iterator
from dataclasses import dataclass, field
from enum import Enum
import logging

from .lean_utils import PriorityQueue, state_complexity
from .tactic_generator import TacticGenerator, generate_tactics


logger = logging.getLogger(__name__)


class ExplorationResult(Enum):
    """Результат исследования."""
    SUCCESS = "success"  # Нашли доказательство
    TIMEOUT = "timeout"  # Превышено время
    MAX_STEPS = "max_steps"  # Превышено число шагов
    NO_PROGRESS = "no_progress"  # Не удалось продвинуться


@dataclass
class StateNode:
    """Узел в графе состояний."""
    pp: str  # Pretty-printed state
    parents: List["StateNode"] = field(default_factory=list)
    tactics_from_parents: List[str] = field(default_factory=list)
    depth: int = 0  # Глубина от начального состояния
    is_proof_finished: bool = False


@dataclass
class TrainingPair:
    """Пара (state, tactic) для обучения."""
    state: str  # Состояние перед применением тактики
    tactic: str  # Тактика
    next_state: str  # Состояние после (или "ProofFinished")
    distance_to_proof: int  # Расстояние до ProofFinished (-1 если неизвестно)
    theorem_name: str = ""  # Имя исходной теоремы
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "tactic": self.tactic,
            "next_state": self.next_state,
            "distance_to_proof": self.distance_to_proof,
            "theorem_name": self.theorem_name,
        }


@dataclass 
class ExplorationStats:
    """Статистика исследования."""
    total_states: int = 0
    total_tactics_tried: int = 0
    successful_tactics: int = 0
    proof_found: bool = False
    elapsed_time: float = 0.0
    max_depth_reached: int = 0


class StateExplorer:
    """
    Исследователь графа состояний Lean.
    
    Использует BFS для поиска доказательств и сбора обучающих данных.
    
    Поддерживает:
    - Rule-based генерацию тактик (по умолчанию, без ML)
    - ML-ускоренную генерацию (через ml_generator)
    
    Example:
        >>> from lean_dojo import Dojo, Theorem, LeanGitRepo
        >>> repo = LeanGitRepo("https://github.com/...", "commit")
        >>> theorem = Theorem(repo, "path/to/file.lean", "theorem_name")
        >>> explorer = StateExplorer()
        >>> with Dojo(theorem) as (dojo, state_0):
        ...     result, pairs = explorer.explore(dojo, state_0, theorem.full_name)
        
    Example with ML:
        >>> from re_rl.tasks.formal import create_ml_generator
        >>> ml_gen = create_ml_generator("hf", model_name="kaiyuy/leandojo-lean4-tacgen-byt5-small")
        >>> explorer = StateExplorer(ml_generator=ml_gen)
    """
    
    def __init__(
        self,
        max_steps: int = 10000,
        max_time: int = 300,  # 5 минут
        max_depth: int = 15,
        max_states: int = 5000,
        tactic_generator: Optional[TacticGenerator] = None,
        ml_generator: Optional[Any] = None,  # MLTacticGenerator
        tactic_timeout: float = 1.0,  # Таймаут на одну тактику
        verbose: bool = False,
    ):
        """
        Args:
            max_steps: Максимум применений тактик
            max_time: Максимум времени (секунды)
            max_depth: Максимальная глубина поиска
            max_states: Максимум уникальных состояний
            tactic_generator: Rule-based генератор тактик (или по умолчанию)
            ml_generator: ML-based генератор тактик (опционально, для ускорения)
            tactic_timeout: Таймаут на применение одной тактики
            verbose: Подробный вывод
        """
        self.max_steps = max_steps
        self.max_time = max_time
        self.max_depth = max_depth
        self.max_states = max_states
        self.tactic_generator = tactic_generator or TacticGenerator()
        self.ml_generator = ml_generator
        self.tactic_timeout = tactic_timeout
        self.verbose = verbose
    
    def _generate_tactics(self, state_pp: str) -> List[str]:
        """
        Генерирует тактики для состояния.
        
        Использует ML генератор если доступен, иначе rule-based.
        """
        tactics = []
        seen = set()
        
        # 1. ML генератор (если доступен)
        if self.ml_generator is not None:
            try:
                if hasattr(self.ml_generator, 'is_available') and self.ml_generator.is_available():
                    ml_tactics = self.ml_generator.generate(state_pp, num_samples=50)
                    for tactic, score in ml_tactics:
                        if tactic not in seen:
                            tactics.append(tactic)
                            seen.add(tactic)
            except Exception as e:
                if self.verbose:
                    logger.warning(f"ML generator failed: {e}")
        
        # 2. Rule-based генератор (дополняем или используем как fallback)
        rule_tactics = self.tactic_generator.generate(state_pp)
        for tactic in rule_tactics:
            if tactic not in seen:
                tactics.append(tactic)
                seen.add(tactic)
        
        return tactics
    
    def explore(
        self,
        dojo: Any,  # lean_dojo.Dojo
        state_0: Any,  # Initial TacticState
        theorem_name: str = "",
        exit_on_proof: bool = False,  # Остановиться после первого доказательства?
    ) -> Tuple[ExplorationResult, List[TrainingPair], ExplorationStats]:
        """
        Исследует граф состояний начиная с state_0.
        
        Args:
            dojo: LeanDojo Dojo instance
            state_0: Начальное состояние
            theorem_name: Имя теоремы (для метаданных)
            exit_on_proof: Остановиться после первого доказательства
            
        Returns:
            (result, training_pairs, stats)
        """
        start_time = time.time()
        stats = ExplorationStats()
        
        # Структуры данных
        queue = PriorityQueue()
        state_dict: Dict[str, StateNode] = {}  # pp -> StateNode
        proof_finished_nodes: List[StateNode] = []
        
        # Добавляем начальное состояние
        initial_node = StateNode(pp=state_0.pp, depth=0)
        state_dict[state_0.pp] = initial_node
        queue.push((state_0, initial_node), state_complexity(state_0.pp))
        
        n_steps = 0
        
        while queue:
            # Проверяем лимиты
            elapsed = time.time() - start_time
            if elapsed > self.max_time:
                if self.verbose:
                    logger.info(f"Timeout after {elapsed:.1f}s")
                stats.elapsed_time = elapsed
                break
            
            if n_steps >= self.max_steps:
                if self.verbose:
                    logger.info(f"Max steps reached: {n_steps}")
                break
            
            if len(state_dict) >= self.max_states:
                if self.verbose:
                    logger.info(f"Max states reached: {len(state_dict)}")
                break
            
            # Извлекаем состояние с наименьшей сложностью
            item = queue.pop()
            if item is None:
                break
            
            curr_state, curr_node = item
            
            # Пропускаем если слишком глубоко
            if curr_node.depth >= self.max_depth:
                continue
            
            stats.max_depth_reached = max(stats.max_depth_reached, curr_node.depth)
            
            # Генерируем тактики для этого состояния (ML + rules)
            tactics = self._generate_tactics(curr_state.pp)
            
            for tactic in tactics:
                n_steps += 1
                stats.total_tactics_tried += 1
                
                if n_steps % 1000 == 0 and self.verbose:
                    logger.info(f"Step {n_steps}, states: {len(state_dict)}")
                
                # Применяем тактику
                try:
                    result = self._run_tactic_safe(dojo, curr_state, tactic)
                except Exception as e:
                    continue
                
                if result is None:
                    continue
                
                # Проверяем результат
                result_type = type(result).__name__
                
                if result_type == "ProofFinished":
                    # Нашли доказательство!
                    stats.successful_tactics += 1
                    stats.proof_found = True
                    
                    finished_node = StateNode(
                        pp="ProofFinished",
                        parents=[curr_node],
                        tactics_from_parents=[tactic],
                        depth=curr_node.depth + 1,
                        is_proof_finished=True,
                    )
                    proof_finished_nodes.append(finished_node)
                    
                    if self.verbose:
                        logger.info(f"Proof found! Depth: {finished_node.depth}")
                    
                    if exit_on_proof:
                        break
                
                elif hasattr(result, 'pp'):
                    # Новое валидное состояние
                    new_pp = result.pp
                    
                    if new_pp in state_dict:
                        # Уже видели это состояние — добавляем альтернативный путь
                        existing_node = state_dict[new_pp]
                        if curr_node not in existing_node.parents:
                            existing_node.parents.append(curr_node)
                            existing_node.tactics_from_parents.append(tactic)
                    else:
                        # Новое состояние
                        stats.successful_tactics += 1
                        
                        new_node = StateNode(
                            pp=new_pp,
                            parents=[curr_node],
                            tactics_from_parents=[tactic],
                            depth=curr_node.depth + 1,
                        )
                        state_dict[new_pp] = new_node
                        
                        # Добавляем в очередь с приоритетом
                        complexity = state_complexity(new_pp) + curr_node.depth
                        queue.push((result, new_node), complexity + random.randint(0, 3))
            
            if exit_on_proof and proof_finished_nodes:
                break
        
        # Собираем статистику
        stats.total_states = len(state_dict)
        stats.elapsed_time = time.time() - start_time
        
        # Извлекаем обучающие пары
        training_pairs = self._extract_training_pairs(
            state_dict, 
            proof_finished_nodes,
            theorem_name,
        )
        
        # Определяем результат
        if proof_finished_nodes:
            result = ExplorationResult.SUCCESS
        elif time.time() - start_time > self.max_time:
            result = ExplorationResult.TIMEOUT
        elif n_steps >= self.max_steps:
            result = ExplorationResult.MAX_STEPS
        else:
            result = ExplorationResult.NO_PROGRESS
        
        return result, training_pairs, stats
    
    def _run_tactic_safe(self, dojo: Any, state: Any, tactic: str) -> Optional[Any]:
        """
        Безопасно применяет тактику с таймаутом.
        
        Returns:
            Результат или None при ошибке
        """
        try:
            result = dojo.run_tac(state, tactic)
            
            # Проверяем на ошибки Lean
            result_type = type(result).__name__
            error_types = [
                "LeanError", "TimeoutError", "TacticResult",
                "DojoCrashError", "DojoHardTimeoutError", 
                "DojoInitError", "ProofGivenUp"
            ]
            
            if result_type in error_types:
                return None
            
            return result
            
        except Exception as e:
            return None
    
    def _extract_training_pairs(
        self,
        state_dict: Dict[str, StateNode],
        proof_finished_nodes: List[StateNode],
        theorem_name: str,
    ) -> List[TrainingPair]:
        """
        Извлекает обучающие пары из графа состояний.
        
        Фокусируется на путях, ведущих к ProofFinished.
        """
        pairs: List[TrainingPair] = []
        
        # Обратный обход от ProofFinished
        for finished_node in proof_finished_nodes:
            visited = set()
            self._collect_pairs_backward(
                finished_node, 
                pairs, 
                visited, 
                theorem_name,
                distance=0,
            )
        
        # Также добавляем пары из неуспешных путей (negative examples)
        # но с distance_to_proof = -1
        for pp, node in state_dict.items():
            if node.is_proof_finished:
                continue
            
            for parent, tactic in zip(node.parents, node.tactics_from_parents):
                pair = TrainingPair(
                    state=parent.pp,
                    tactic=tactic,
                    next_state=node.pp,
                    distance_to_proof=-1,  # Неизвестно
                    theorem_name=theorem_name,
                )
                # Добавляем только если этой пары ещё нет
                if not any(p.state == pair.state and p.tactic == pair.tactic for p in pairs):
                    pairs.append(pair)
        
        return pairs
    
    def _collect_pairs_backward(
        self,
        node: StateNode,
        pairs: List[TrainingPair],
        visited: Set[str],
        theorem_name: str,
        distance: int,
    ):
        """Рекурсивно собирает пары обратным обходом."""
        if node.pp in visited:
            return
        visited.add(node.pp)
        
        for parent, tactic in zip(node.parents, node.tactics_from_parents):
            pair = TrainingPair(
                state=parent.pp,
                tactic=tactic,
                next_state=node.pp if not node.is_proof_finished else "ProofFinished",
                distance_to_proof=distance,
                theorem_name=theorem_name,
            )
            pairs.append(pair)
            
            # Рекурсия к родителям
            self._collect_pairs_backward(
                parent, pairs, visited, theorem_name, distance + 1
            )


def explore_theorem(
    theorem: Any,  # lean_dojo.Theorem
    max_steps: int = 5000,
    max_time: int = 120,
    verbose: bool = False,
) -> Tuple[ExplorationResult, List[TrainingPair], ExplorationStats]:
    """
    Удобная функция для исследования одной теоремы.
    
    Args:
        theorem: LeanDojo Theorem object
        max_steps: Максимум шагов
        max_time: Максимум времени
        verbose: Подробный вывод
        
    Returns:
        (result, training_pairs, stats)
        
    Example:
        >>> from lean_dojo import Theorem, LeanGitRepo
        >>> repo = LeanGitRepo("https://github.com/leanprover-community/mathlib4", "...")
        >>> theorem = Theorem(repo, "Mathlib/Algebra/Basic.lean", "add_comm")
        >>> result, pairs, stats = explore_theorem(theorem)
    """
    # Импортируем здесь чтобы не требовать lean_dojo при импорте модуля
    try:
        from lean_dojo import Dojo
    except ImportError:
        raise ImportError(
            "LeanDojo is required for state exploration. "
            "Install with: pip install lean-dojo"
        )
    
    explorer = StateExplorer(
        max_steps=max_steps,
        max_time=max_time,
        verbose=verbose,
    )
    
    with Dojo(theorem) as (dojo, state_0):
        return explorer.explore(
            dojo, 
            state_0, 
            theorem_name=theorem.full_name,
            exit_on_proof=False,
        )
