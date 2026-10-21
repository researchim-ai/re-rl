# re_rl/tasks/generators.py

import random
import sympy
from typing import Optional

# ============================================================================
# ИМПОРТЫ МАТЕМАТИЧЕСКИХ ЗАДАЧ
# ============================================================================

# Алгебра
from re_rl.tasks.math.algebra.linear_task import LinearTask
from re_rl.tasks.math.algebra.quadratic_task import QuadraticTask
from re_rl.tasks.math.algebra.cubic_task import CubicTask
from re_rl.tasks.math.algebra.system_linear_task import SystemLinearTask
from re_rl.tasks.math.algebra.exponential_task import ExponentialTask
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask
from re_rl.tasks.math.algebra.inequality_task import InequalityTask
from re_rl.tasks.math.algebra.symbolic_simplification_task import SymbolicSimplificationTask

# Анализ
from re_rl.tasks.math.analysis.calculus_task import CalculusTask
from re_rl.tasks.math.analysis.limits_task import LimitsTask
from re_rl.tasks.math.analysis.integral_task import IntegralTask
from re_rl.tasks.math.analysis.differential_equation_task import DifferentialEquationTask
from re_rl.tasks.math.analysis.series_task import SeriesTask
from re_rl.tasks.math.analysis.optimization_task import OptimizationTask

# Геометрия
from re_rl.tasks.math.geometry.geometry_task import GeometryTask
from re_rl.tasks.math.geometry.trigonometry_task import TrigonometryTask
from re_rl.tasks.math.geometry.vector_3d_task import Vector3DTask

# Линейная алгебра
from re_rl.tasks.math.linear_algebra.matrix_task import MatrixTask
from re_rl.tasks.math.linear_algebra.complex_number_task import ComplexNumberTask

# Дискретная математика
from re_rl.tasks.math.discrete.number_theory_task import NumberTheoryTask
from re_rl.tasks.math.discrete.combinatorics_task import CombinatoricsTask
from re_rl.tasks.math.discrete.sequence_task import SequenceTask
from re_rl.tasks.math.discrete.set_logic_task import SetLogicTask
from re_rl.tasks.math.discrete.graph_task import GraphTask

# Абстрактная алгебра
from re_rl.tasks.math.abstract_algebra.group_theory_task import GroupTheoryTask
from re_rl.tasks.math.abstract_algebra.category_theory_task import CategoryTheoryTask

# Вероятность и статистика
from re_rl.tasks.math.probability.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.math.probability.statistics_task import StatisticsTask
from re_rl.tasks.math.probability.bayesian_reasoning_task import BayesianReasoningTask

# Прикладная математика
from re_rl.tasks.math.applied.financial_math_task import FinancialMathTask
from re_rl.tasks.math.applied.arithmetic_task import ArithmeticTask

# Логика
from re_rl.tasks.math.logic.contradiction_task import ContradictionTask
from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.math.logic.futoshiki_task import FutoshikiTask
from re_rl.tasks.math.logic.analogical_task import AnalogicalTask
from re_rl.tasks.math.logic.text_stats_task import TextStatsTask
from re_rl.tasks.math.logic.sudoku_task import SudokuTask
from re_rl.tasks.math.logic.zebra_puzzle_task import ZebraPuzzleTask
from re_rl.tasks.math.logic.csp_reasoning_task import CSPReasoningTask
from re_rl.tasks.math.logic.sat_smt_mini_task import SATSMTMiniTask
from re_rl.tasks.math.logic.proof_cases_counterexample_task import ProofCasesCounterexampleTask
from re_rl.tasks.math.logic.find_the_error_task import FindTheErrorTask
from re_rl.tasks.math.logic.propositional_logic_task import PropositionalLogicTask
from re_rl.tasks.math.logic.regex_dfa_task import RegexDFATask
from re_rl.tasks.math.discrete.dynamic_programming_task import DynamicProgrammingTask
from re_rl.tasks.math.logic.cryptarithmetic_task import CryptarithmeticTask
from re_rl.tasks.math.logic.inequality_proof_task import InequalityProofTask

# Волна «ризонинг-задачи»
from re_rl.tasks.math.logic.graph_reasoning_task import GraphReasoningTask
from re_rl.tasks.math.logic.ordering_puzzle_task import OrderingPuzzleTask
from re_rl.tasks.math.logic.state_tracking_task import StateTrackingTask
from re_rl.tasks.math.logic.grid_navigation_task import GridNavigationTask
from re_rl.tasks.math.logic.interval_scheduling_task import IntervalSchedulingTask
from re_rl.tasks.math.logic.set_reasoning_task import SetReasoningTask
from re_rl.tasks.math.logic.pattern_induction_task import PatternInductionTask
from re_rl.tasks.math.logic.syllogism_task import SyllogismTask
from re_rl.tasks.math.logic.logical_entailment_task import LogicalEntailmentTask
from re_rl.tasks.math.logic.boolean_circuit_task import BooleanCircuitTask
from re_rl.tasks.math.logic.mastermind_task import MastermindTask
from re_rl.tasks.math.logic.countdown_24_task import Countdown24Task
from re_rl.tasks.math.logic.game_theory_optimal_task import GameTheoryOptimalTask
from re_rl.tasks.math.logic.family_tree_task import FamilyTreeTask
from re_rl.tasks.math.logic.minesweeper_deduction_task import MinesweeperDeductionTask
from re_rl.tasks.math.logic.n_queens_task import NQueensTask
from re_rl.tasks.math.logic.magic_square_task import MagicSquareTask
from re_rl.tasks.math.logic.skyscrapers_task import SkyscrapersTask
from re_rl.tasks.math.logic.kenken_task import KenKenTask
from re_rl.tasks.math.logic.kakuro_task import KakuroTask

# Волна «графы / оптимизация / симуляция / сетки / дедукция / игры / пространство»
from re_rl.tasks.math.logic.graph_algorithms_task import (
    WeightedShortestPathTask, TopologicalSortTask, GraphColoringTask, MSTWeightTask,
    EulerianPathTask, HamiltonianPathTask, BipartiteMatchingTask, TSPTask, MaxFlowTask,
    DAGLongestPathTask,
)
from re_rl.tasks.math.logic.optimization_task import KnapsackTask, SubsetSumTask
from re_rl.tasks.math.logic.formal_logic2_task import (
    TruthTableTask, ModelCountingTask, ThreeSatTask, LogicalEquivalenceTask, QBFTask,
)
from re_rl.tasks.math.logic.automata_sim_task import (
    DFASimulationTask, TuringMachineTask, GameOfLifeTask, ElementaryCATask,
)
from re_rl.tasks.math.logic.algo_sim_task import (
    RPNEvalTask, BalancedBracketsTask, SortingTraceTask,
)
from re_rl.tasks.math.logic.grids2_task import (
    NonogramTask, BinaryPuzzleTask, HitoriTask, StarBattleTask, BattleshipTask,
)
from re_rl.tasks.math.logic.deduction2_task import (
    LogicGridTask, SeatingCircularTask, TournamentTask,
)
from re_rl.tasks.math.logic.games2_task import CombinatorialGamesTask, TicTacToeTask
from re_rl.tasks.math.logic.spatial_task import (
    CubeNetTask, DiceReasoningTask, RotationReflectionTask, PaperFoldingTask,
)
from re_rl.tasks.math.logic.misc_logic_task import (
    CipherDecodeTask, PigeonholeTask, MontyHallTask, AllenRelationsTask,
)

# Волна «продвинутый ризонинг»
from re_rl.tasks.math.logic.arc_induction_task import ARCGridInductionTask
from re_rl.tasks.math.logic.program_trace_task import ProgramTraceTask
from re_rl.tasks.math.logic.sprague_grundy_task import SpragueGrundyTask
from re_rl.tasks.math.logic.natural_deduction_task import NaturalDeductionTask
from re_rl.tasks.math.logic.string_dp_task import EditDistanceTask
from re_rl.tasks.math.logic.calendar_task import CalendarReasoningTask
from re_rl.tasks.math.logic.word_ladder_task import WordLadderTask
from re_rl.tasks.math.logic.cfg_membership_task import CFGMembershipTask
from re_rl.tasks.math.logic.datalog_inference_task import DatalogInferenceTask
from re_rl.tasks.math.logic.unification_task import UnificationTask
from re_rl.tasks.math.logic.lambda_calculus_task import LambdaCalculusTask
from re_rl.tasks.math.logic.resolution_task import ResolutionTask
from re_rl.tasks.math.logic.lis_dp_task import LISDPTask
from re_rl.tasks.math.logic.kmp_matching_task import KMPMatchingTask
from re_rl.tasks.math.logic.sliding_puzzle_task import SlidingPuzzleTask
from re_rl.tasks.math.logic.connect_four_task import ConnectFourTask
from re_rl.tasks.math.logic.graph_connectivity_task import GraphConnectivityTask
from re_rl.tasks.math.logic.huffman_task import HuffmanCodingTask
from re_rl.tasks.math.logic.dfa_minimization_task import DFAMinimizationTask
from re_rl.tasks.math.logic.stable_matching_task import StableMatchingTask
from re_rl.tasks.math.logic.hamming_code_task import HammingCodeTask
from re_rl.tasks.math.logic.page_replacement_task import PageReplacementTask
from re_rl.tasks.math.logic.tree_queries_task import TreeQueriesTask
from re_rl.tasks.math.logic.os_scheduling_task import OSSchedulingTask
from re_rl.tasks.math.logic.fractional_knapsack_task import FractionalKnapsackTask
from re_rl.tasks.math.logic.cache_task import DirectMappedCacheTask
from re_rl.tasks.math.logic.knight_moves_task import KnightMovesTask
from re_rl.tasks.ml.entropy_task import ShannonEntropyTask
from re_rl.tasks.ml.gini_task import GiniSplitTask
from re_rl.tasks.ml.knn_task import KNNClassifyTask
from re_rl.tasks.ml.perceptron_task import PerceptronUpdateTask
from re_rl.tasks.ml.kmeans_task import KMeansStepTask
from re_rl.tasks.ml.naive_bayes_task import NaiveBayesTask
from re_rl.tasks.ml.confusion_task import ConfusionMetricsTask
from re_rl.tasks.ml.gradient_step_task import GradientStepTask
from re_rl.tasks.ml.ranking_auc_task import RankingAUCTask
from re_rl.tasks.ml.hinge_task import HingeLossTask
from re_rl.tasks.ml.cosine_task import CosineRankTask
from re_rl.tasks.ml.univariate_regression_task import UnivariateRegressionTask
from re_rl.tasks.ml.decision_stump_task import DecisionStumpTask
from re_rl.tasks.ml.brier_task import BrierScoreTask
from re_rl.tasks.ml.mse_task import MseTask
from re_rl.tasks.ml.precision_at_k_task import PrecisionAtKTask
from re_rl.tasks.ml.kappa_task import CohenKappaTask
from re_rl.tasks.ml.r2_task import R2Task
from re_rl.tasks.ml.average_precision_task import AveragePrecisionTask
from re_rl.tasks.ml.mae_task import MaeTask
from re_rl.tasks.ml.jaccard_task import JaccardTask
from re_rl.tasks.ml.reciprocal_rank_task import ReciprocalRankTask
from re_rl.tasks.ml.kalman_task import KalmanUpdateTask
from re_rl.tasks.ml.hmm_task import HmmDecodeTask
from re_rl.tasks.ml.elimination_task import EliminationQueryTask
from re_rl.tasks.ml.pagerank_task import PageRankTask
from re_rl.tasks.math.discrete.catalan_task import CatalanTask
from re_rl.tasks.math.discrete.stirling_task import StirlingSecondTask
from re_rl.tasks.math.discrete.gray_code_task import GrayCodeTask
from re_rl.tasks.math.logic.binary_search_task import BinarySearchTask
from re_rl.tasks.math.logic.matrix_chain_task import MatrixChainTask
from re_rl.tasks.math.logic.common_substring_task import CommonSubstringTask
from re_rl.tasks.math.geometry.solid_volume_task import SolidVolumeTask
from re_rl.tasks.math.logic.round_robin_task import RoundRobinTask
from re_rl.tasks.math.logic.deadlock_task import DeadlockTask
from re_rl.tasks.math.logic.second_price_task import SecondPriceTask
from re_rl.tasks.math.logic.shapley_task import ShapleyValueTask
from re_rl.tasks.math.logic.max_subarray_task import MaxSubarrayTask
from re_rl.tasks.math.logic.house_robber_task import HouseRobberTask
from re_rl.tasks.math.logic.rod_cutting_task import RodCuttingTask
from re_rl.tasks.math.logic.pair_sum_task import PairSumTask
from re_rl.tasks.math.logic.heap_task import HeapTask
from re_rl.tasks.math.logic.weighted_interval_task import WeightedIntervalTask
from re_rl.tasks.rl.discounted_return_task import DiscountedReturnTask
from re_rl.tasks.rl.q_learning_task import QLearningTask
from re_rl.tasks.rl.bellman_task import BellmanBackupTask
from re_rl.tasks.rl.sarsa_task import SarsaTask
from re_rl.tasks.rl.epsilon_greedy_task import EpsilonGreedyTask
from re_rl.tasks.rl.policy_expectation_task import PolicyExpectationTask
from re_rl.tasks.rl.reward_to_go_task import RewardToGoTask
from re_rl.tasks.rl.double_q_task import DoubleQTask
from re_rl.tasks.rl.polyak_task import PolyakTask
from re_rl.tasks.rl.eligibility_task import EligibilityTraceTask
from re_rl.tasks.rl.expected_sarsa_task import ExpectedSarsaTask
from re_rl.tasks.rl.gae_task import GaeTask
from re_rl.tasks.rl.ppo_task import PpoClipTask
from re_rl.tasks.rl.importance_task import ImportanceRatioTask
from re_rl.tasks.rl.average_reward_task import AverageRewardTask
from re_rl.tasks.rl.vtrace_task import VTraceTask
from re_rl.tasks.rl.priority_replay_task import PriorityReplayTask
from re_rl.tasks.rl.reward_clip_task import RewardClipTask
from re_rl.tasks.rl.finite_horizon_task import FiniteHorizonTask
from re_rl.tasks.rl.q_trajectory_task import QTrajectoryTask
from re_rl.tasks.rl.sarsa_trajectory_task import SarsaTrajectoryTask
from re_rl.tasks.rl.double_q_trajectory_task import DoubleQTrajectoryTask
from re_rl.tasks.math.logic.min_path_sum_task import MinPathSumTask
from re_rl.tasks.math.logic.stock_profit_task import StockProfitTask
from re_rl.tasks.math.logic.jump_game_task import JumpGameTask
from re_rl.tasks.math.logic.container_water_task import ContainerWaterTask
from re_rl.tasks.math.logic.decode_ways_task import DecodeWaysTask
from re_rl.tasks.math.logic.gas_station_task import GasStationTask
from re_rl.tasks.math.logic.dag_paths_task import DagPathsTask
from re_rl.tasks.math.logic.shortest_count_task import ShortestCountTask
from re_rl.tasks.math.logic.triangle_girth_task import TriangleGirthTask
from re_rl.tasks.math.logic.wiener_task import WienerTask
from re_rl.tasks.math.logic.tree_radius_task import TreeRadiusTask
from re_rl.tasks.math.logic.prufer_task import PruferTask
from re_rl.tasks.math.logic.havel_hakimi_task import HavelHakimiTask
from re_rl.tasks.math.logic.spanning_trees_task import SpanningTreesTask
from re_rl.tasks.math.logic.topo_count_task import TopoCountTask
from re_rl.tasks.math.geometry.pick_theorem_task import PickTheoremTask
from re_rl.tasks.math.logic.trapping_rain_task import TrappingRainTask
from re_rl.tasks.math.logic.majority_task import MajorityTask
from re_rl.tasks.math.discrete.euclid_task import EuclidTask
from re_rl.tasks.math.discrete.josephus_task import JosephusTask
from re_rl.tasks.math.discrete.collatz_task import CollatzTask
from re_rl.tasks.math.logic.histogram_task import HistogramTask
from re_rl.tasks.math.logic.target_sum_task import TargetSumTask
from re_rl.tasks.math.logic.stock_unlimited_task import StockUnlimitedTask
from re_rl.tasks.math.logic.palindrome_subseq_task import PalindromeSubseqTask
from re_rl.tasks.math.logic.subarray_sum_task import SubarraySumTask
from re_rl.tasks.math.logic.max_product_task import MaxProductTask
from re_rl.tasks.math.logic.min_assignment_task import MinAssignmentTask
from re_rl.tasks.math.logic.floyd_distance_task import FloydDistanceTask
from re_rl.tasks.math.logic.sequence_alignment_task import SequenceAlignmentTask
from re_rl.tasks.math.logic.range_query_task import RangeQueryTask
from re_rl.tasks.math.logic.mixed_nash_task import MixedNashTask
from re_rl.tasks.math.logic.expectimax_task import ExpectimaxTask
from re_rl.tasks.math.logic.minimax_tree_task import MinimaxTreeTask
from re_rl.tasks.math.logic.local_alignment_task import LocalAlignmentTask
from re_rl.tasks.math.logic.nussinov_task import NussinovTask
from re_rl.tasks.math.logic.optimal_bst_task import OptimalBstTask
from re_rl.tasks.math.logic.alpha_beta_task import AlphaBetaTask
from re_rl.tasks.math.logic.polynomial_product_task import PolynomialProductTask
from re_rl.tasks.math.logic.range_add_task import RangeAddTask
from re_rl.tasks.math.logic.tree_mis_task import TreeMisTask
from re_rl.tasks.math.logic.subsequence_count_task import SubsequenceCountTask
from re_rl.tasks.math.discrete.secret_share_task import SecretShareTask
from re_rl.tasks.math.discrete.integer_sqrt_task import IntegerSqrtTask
from re_rl.tasks.math.discrete.min_squares_task import MinSquaresTask
from re_rl.tasks.math.geometry.computational_geometry_task import ComputationalGeometryTask
from re_rl.tasks.math.analysis.symbolic_regression_task import SymbolicRegressionTask
from re_rl.tasks.math.analysis.numerical_methods_task import NumericalMethodsTask
from re_rl.tasks.math.analysis.lagrange_task import LagrangeInterpolationTask
from re_rl.tasks.math.analysis.euler_method_task import EulerMethodTask
from re_rl.tasks.math.algebra.polynomial_factorization_task import PolynomialFactorizationTask
from re_rl.tasks.math.discrete.base_conversion_task import BaseConversionTask
from re_rl.tasks.math.discrete.modular_arithmetic_task import ModularArithmeticTask
from re_rl.tasks.math.linear_algebra.matrix_reasoning_task import MatrixReasoningTask
# Волна «важная математика»
from re_rl.tasks.math.analysis.taylor_series_task import TaylorSeriesTask
from re_rl.tasks.math.analysis.partial_fractions_task import PartialFractionsTask
from re_rl.tasks.math.analysis.partial_derivatives_task import PartialDerivativesTask
from re_rl.tasks.math.analysis.area_between_curves_task import AreaBetweenCurvesTask
from re_rl.tasks.math.analysis.lhopital_task import LHopitalTask
from re_rl.tasks.math.discrete.recurrence_task import RecurrenceTask
from re_rl.tasks.math.discrete.complexity_task import AlgorithmComplexityTask
from re_rl.tasks.math.discrete.min_coins_task import MinCoinsTask
from re_rl.tasks.math.discrete.union_find_task import UnionFindTask
from re_rl.tasks.math.discrete.twos_complement_task import TwosComplementTask
from re_rl.tasks.math.discrete.prime_factorization_task import PrimeFactorizationTask
from re_rl.tasks.math.discrete.diophantine_task import DiophantineTask
from re_rl.tasks.math.discrete.modular_inverse_task import ModularInverseTask
from re_rl.tasks.math.discrete.continued_fraction_task import ContinuedFractionTask
from re_rl.tasks.math.discrete.generating_function_task import GeneratingFunctionTask
from re_rl.tasks.math.linear_algebra.gaussian_elimination_task import GaussianEliminationTask
from re_rl.tasks.math.linear_algebra.matrix_multiplication_task import MatrixMultiplicationTask
from re_rl.tasks.math.linear_algebra.gram_schmidt_task import GramSchmidtTask
from re_rl.tasks.math.linear_algebra.least_squares_task import LeastSquaresTask
from re_rl.tasks.math.linear_algebra.roots_of_unity_task import RootsOfUnityTask
from re_rl.tasks.math.probability.expected_value_task import ExpectedValueTask
from re_rl.tasks.math.probability.markov_chain_task import MarkovChainTask
from re_rl.tasks.math.probability.conditional_probability_task import ConditionalProbabilityTask
from re_rl.tasks.math.probability.hypothesis_testing_task import HypothesisTestingTask
from re_rl.tasks.math.geometry.coordinate_geometry_task import CoordinateGeometryTask
from re_rl.tasks.math.geometry.shoelace_area_task import ShoelaceAreaTask
from re_rl.tasks.math.geometry.triangle_solving_task import TriangleSolvingTask
from re_rl.tasks.math.geometry.conic_sections_task import ConicSectionsTask
from re_rl.tasks.math.algebra.vieta_task import VietaTask

# Планирование
from re_rl.tasks.math.planning.river_crossing_task import RiverCrossingTask
from re_rl.tasks.math.planning.tower_of_hanoi_task import TowerOfHanoiTask
from re_rl.tasks.math.planning.water_jug_task import WaterJugTask
from re_rl.tasks.math.planning.blocks_world_task import BlocksWorldTask

# Теория игр
from re_rl.tasks.math.discrete.nim_game_task import NimGameTask
from re_rl.tasks.math.discrete.graph_justification_task import GraphJustificationTask
from re_rl.tasks.math.discrete.combinatorial_optimization_task import CombinatorialOptimizationTask

# Физические задачи (импортируем все генераторы)
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS

# Формальная математика (Lean 4 доказательства)
from re_rl.tasks.formal.lean_proof_task import (
    LeanProofTask,
    generate_lean_proof_task,
    generate_lean_proof_batch,
)


##################################################
# 0. Арифметические задачи (цепочки операций)
##################################################

def generate_random_arithmetic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    augment: bool = True,
    **kwargs
) -> ArithmeticTask:
    """
    Генерирует случайную арифметическую задачу с цепочками операций.
    
    :param language: 'ru' или 'en'
    :param detail_level: сколько шагов решения показывать
    :param difficulty: уровень сложности (1-10)
    :param augment: если True — использует случайные варианты формулировок
    :return: экземпляр ArithmeticTask
    """
    return ArithmeticTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        augment=augment,
        **kwargs
    )


##################################################
# 1. Линейное уравнение: a*x + b = c
##################################################

def generate_random_linear_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text",
    augment: bool = True,
    a_range=(-10, 10),
    b_range=(-10, 10),
    c_range=(-10, 10),
    **kwargs
) -> LinearTask:
    """
    Генерирует случайную линейную задачу вида a*x + b = c.
    
    Args:
        language: Язык ("ru" или "en")
        detail_level: Сколько шагов решения показывать
        difficulty: Уровень сложности (1-10)
        output_format: Формат вывода ("text" или "latex")
        augment: Если True — использует случайные варианты формулировок
    """
    return LinearTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format,
        augment=augment,
        **kwargs
    )


##################################################
# 2. Квадратное уравнение: a*x^2 + b*x + c = 0
##################################################

def generate_random_quadratic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text",
    augment: bool = True,
    a_range=(-5, 5),
    b_range=(-10, 10),
    c_range=(-10, 10),
    **kwargs
) -> QuadraticTask:
    """
    Генерирует случайную квадратную задачу a*x^2 + b*x + c = 0, a!=0.
    
    Args:
        language: Язык ("ru" или "en")
        detail_level: Детализация решения
        difficulty: Уровень сложности (1-10)
        output_format: Формат вывода ("text" или "latex")
        augment: Если True — использует случайные варианты формулировок
    """
    return QuadraticTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format,
        augment=augment,
        **kwargs
    )


##################################################
# 3. Кубическое уравнение: a*x^3 + b*x^2 + c*x + d
##################################################

def generate_random_cubic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> CubicTask:
    return CubicTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 4. Экспоненциальное уравнение: a*exp(b*x) + c = d
##################################################

def generate_random_exponential_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> ExponentialTask:
    return ExponentialTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 5. Логарифмическое уравнение: a*log(b*x) + c = d
##################################################

def generate_random_logarithmic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> LogarithmicTask:
    return LogarithmicTask(
        difficulty=difficulty,
        language=language,
        detail_level=detail_level,
        output_format=output_format
    )


##################################################
# 6. CalculusTask (дифференцирование / интегрирование)
##################################################

def generate_random_calculus_task(
    task_type="differentiation",
    language="ru",
    detail_level=3,
    difficulty: int = 5,
    output_format: str = "text"
,
    **kwargs
) -> CalculusTask:
    return CalculusTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        output_format=output_format
    )


##################################################
# 7. ContradictionTask
##################################################

def generate_random_contradiction_task(
    language="ru",
    num_statements=10,
    reasoning_mode: bool = False,
    **kwargs  # игнорируем difficulty и другие
) -> ContradictionTask:
    return ContradictionTask(language=language, num_statements=num_statements, reasoning_mode=reasoning_mode)


##################################################
# 8. KnightsKnavesTask
##################################################

def generate_random_knights_knaves_task(
    language="ru",
    detail_level=5,
    reasoning_mode: bool = False,
    **kwargs
) -> KnightsKnavesTask:
    return KnightsKnavesTask(language=language, detail_level=detail_level, reasoning_mode=reasoning_mode)


##################################################
# 9. FutoshikiTask
##################################################

def generate_random_futoshiki_task(
    language="ru",
    detail_level=5,
    size_range=(4,5),
    ineq_factor=2,
    reasoning_mode: bool = False,
    **kwargs
) -> FutoshikiTask:
    """
    size_range=(4,5) => выбираем случайный size=4 или 5.
    num_inequalities ~ size*ineq_factor, 
    но можно сделать случайно.
    """
    import random
    size = random.randint(size_range[0], size_range[1])
    num_ineq = random.randint(size, size*ineq_factor)
    return FutoshikiTask(language=language, detail_level=detail_level, size=size, num_inequalities=num_ineq, reasoning_mode=reasoning_mode)


##################################################
# 10. UrnProbabilityTask
##################################################

def generate_random_urn_probability_task(
    language="ru",
    count_containers_range=(2,4),
    draws_range=(1,3),
    **kwargs
) -> UrnProbabilityTask:
    count_containers = random.randint(count_containers_range[0], count_containers_range[1])
    draws = random.randint(draws_range[0], draws_range[1])
    return UrnProbabilityTask(language=language, count_containers=count_containers, draws=draws)


##################################################
# 11. TextStatsTask
##################################################

def generate_random_text_stats_task(
    language="ru",
    detail_level=3,
    allow_overlapping=None,
    text_gen_mode="mixed",
    reasoning_mode: bool = False,
    **kwargs
) -> TextStatsTask:
    """
    Генерируем случайную задачу на поиск подстроки в тексте.
    allow_overlapping - можно random либо bool
    text_gen_mode = "words", "letters", "mixed"
    """
    import random
    if allow_overlapping is None:
        allow_overlapping = bool(random.getrandbits(1))

    return TextStatsTask(
        language=language,
        detail_level=detail_level,
        allow_overlapping=allow_overlapping,
        text_gen_mode=text_gen_mode,
        reasoning_mode=reasoning_mode,
    )


##################################################
# 12. GraphTask
##################################################

def generate_random_graph_task(
    task_type="shortest_path",
    num_nodes=8,
    edge_prob=0.4,
    language="ru",
    detail_level=3
,
    **kwargs
) -> GraphTask:
    return GraphTask(
        task_type=task_type,
        num_nodes=num_nodes,
        edge_prob=edge_prob,
        language=language,
        detail_level=detail_level
    )


##################################################
# 13. SystemLinearTask
##################################################

def generate_random_system_linear_task(
    language="ru",
    detail_level=3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    size: Optional[int] = None,
    **kwargs
):
    """
    Генерируем систему линейных уравнений размером size x size.
    Матрица shape = (size, size+1).
    Метод Крамера, a!=0 => суммарный дет!=0 (не всегда гарантирован).

    Если ``size`` не задан явно, он выводится из ``difficulty``
    (2 для низкой сложности, до 4 для высокой).
    """
    import numpy as np

    if size is None:
        # difficulty 1-3 -> 2, 4-7 -> 3, 8-10 -> 4
        size = 2 if difficulty <= 3 else (3 if difficulty <= 7 else 4)

    while True:
        # Генерируем случайную матрицу (size x (size+1))
        # Например, коэф из -5..5, ensure not all zero
        mat = np.random.randint(-5, 6, size=(size, size+1))
        # Проверим, что A есть invertible
        A = mat[:, :-1]
        detA = round(np.linalg.det(A), 5)
        if abs(detA) < 1e-3:
            continue
        return SystemLinearTask(mat.tolist(), language=language, detail_level=detail_level)


##################################################
# 14. AnalogicalTask
##################################################

def generate_random_analogical_task(
    language: str = "ru",
    detail_level: int = 3,
    reasoning_mode: bool = False,
    **kwargs
) -> AnalogicalTask:
    """
    Генерирует случайную аналогическую задачу.
    
    :param language: 'ru' или 'en'
    :param detail_level: количество шагов в решении
    :param reasoning_mode: режим рассуждений
    :return: экземпляр AnalogicalTask
    """
    # Список предопределенных аналогий
    analogies = [
        # Математические аналогии
        "2 * 3 = 6 -> 3 * 4 = 12",
        "2^3 = 8 -> 3^2 = 9",
        "5 + 3 = 8 -> 7 + 4 = 11",
        
        # Логические аналогии
        "круг -> круглый -> квадрат -> квадратный",
        "бежать -> бег -> плыть -> плавание",
        "горячий -> холодный -> светлый -> темный",
        
        # Геометрические аналогии
        "треугольник -> 3 стороны -> квадрат -> 4 стороны",
        "круг -> 0 углов -> треугольник -> 3 угла",
        
        # Числовые аналогии
        "2 -> 4 -> 3 -> 6",  # умножение на 2
        "3 -> 9 -> 4 -> 16",  # возведение в квадрат
        "2 -> 8 -> 3 -> 27",  # возведение в куб
    ]
    
    # Выбираем случайную аналогию
    analogy = random.choice(analogies)
    
    return AnalogicalTask(
        description=analogy,
        language=language,
        detail_level=detail_level,
        reasoning_mode=reasoning_mode
    )


##################################################
# 15. GroupTheoryTask
##################################################

def generate_random_group_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    task_type=None,
    group_type=None
,
    **kwargs
) -> GroupTheoryTask:
    """Генерируем случайную задачу по теории групп."""
    return GroupTheoryTask.generate_random_task(
        task_type=task_type,
        group_type=group_type,
        language=language,
        detail_level=detail_level
    )

##################################################
# 16. CategoryTheoryTask
##################################################

def generate_random_category_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    task_type=None
,
    **kwargs
) -> CategoryTheoryTask:
    """Генерируем случайную задачу по теории категорий."""
    return CategoryTheoryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level
    )


##################################################
# 17. NumberTheoryTask - Теория чисел
##################################################

def generate_random_number_theory_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> NumberTheoryTask:
    """
    Генерирует случайную задачу по теории чисел.
    
    Типы задач:
    - gcd_lcm: НОД и НОК
    - prime_factorization: разложение на простые множители
    - modular_arithmetic: вычисления по модулю
    - chinese_remainder: китайская теорема об остатках
    - divisibility: делимость
    - diophantine: диофантовы уравнения
    - euler_totient: функция Эйлера
    """
    return NumberTheoryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 18. CombinatoricsTask - Комбинаторика
##################################################

def generate_random_combinatorics_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> CombinatoricsTask:
    """
    Генерирует случайную комбинаторную задачу.
    
    Типы задач:
    - permutations: перестановки
    - combinations: сочетания
    - binomial: биномиальные коэффициенты
    - pigeonhole: принцип Дирихле
    - inclusion_exclusion: формула включения-исключения
    - derangements: беспорядки
    - stars_and_bars: шары и перегородки
    - circular_permutation: круговые перестановки
    """
    return CombinatoricsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 19. SequenceTask - Последовательности
##################################################

def generate_random_sequence_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> SequenceTask:
    """
    Генерирует случайную задачу на последовательности.
    
    Типы задач:
    - arithmetic_nth: n-й член арифметической прогрессии
    - arithmetic_sum: сумма арифметической прогрессии
    - geometric_nth: n-й член геометрической прогрессии
    - geometric_sum: сумма геометрической прогрессии
    - fibonacci_nth: числа Фибоначчи
    - recurrence: рекуррентные соотношения
    - pattern: найти закономерность
    """
    return SequenceTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 20. GeometryTask - Геометрия
##################################################

def generate_random_geometry_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> GeometryTask:
    """
    Генерирует случайную геометрическую задачу.
    
    Типы задач:
    - triangle_area_coords: площадь треугольника по координатам
    - triangle_area_sides: площадь по формуле Герона
    - distance_2d/3d: расстояние между точками
    - circle_area, circle_circumference: площадь/окружность
    - sphere_volume, cylinder_volume, cone_volume: объёмы тел
    - angle_between_vectors: угол между векторами
    - dot_product, cross_product: произведения векторов
    - line_equation: уравнение прямой
    - midpoint: середина отрезка
    """
    return GeometryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 21. MatrixTask - Матрицы
##################################################

def generate_random_matrix_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> MatrixTask:
    """
    Генерирует случайную задачу с матрицами.
    
    Типы задач:
    - determinant: вычисление определителя
    - inverse: обратная матрица
    - multiplication: умножение матриц
    - transpose: транспонирование
    - rank: ранг матрицы
    - eigenvalues: собственные значения
    - trace: след матрицы
    - add: сложение матриц
    - scalar_mult: умножение на скаляр
    """
    return MatrixTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 22. TrigonometryTask - Тригонометрия
##################################################

def generate_random_trigonometry_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> TrigonometryTask:
    """
    Генерирует случайную тригонометрическую задачу.
    
    Типы задач:
    - basic_value: значения тригонометрических функций
    - equation: тригонометрические уравнения
    - identity: упрощение тождеств
    - triangle_solve: решение треугольников
    - inverse: обратные тригонометрические функции
    """
    return TrigonometryTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 23. InequalityTask - Неравенства
##################################################

def generate_random_inequality_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> InequalityTask:
    """
    Генерирует случайную задачу на неравенства.
    
    Типы задач:
    - linear: линейные неравенства
    - quadratic: квадратные неравенства
    - rational: дробно-рациональные
    - absolute: с модулем
    - system: системы неравенств
    """
    return InequalityTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 24. ComplexNumberTask - Комплексные числа
##################################################

def generate_random_complex_number_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> ComplexNumberTask:
    """
    Генерирует случайную задачу с комплексными числами.
    
    Типы задач:
    - arithmetic: арифметические операции
    - modulus: модуль
    - argument: аргумент
    - polar_form: тригонометрическая форма
    - power: возведение в степень (формула Муавра)
    - roots: корни n-й степени
    - conjugate: сопряжённое число
    - equation: уравнения
    """
    return ComplexNumberTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 25. LimitsTask - Пределы
##################################################

def generate_random_limits_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> LimitsTask:
    """
    Генерирует случайную задачу на пределы.
    
    Типы задач:
    - polynomial: пределы полиномов
    - rational: пределы рациональных функций
    - infinity: пределы на бесконечности
    - indeterminate: неопределённости (0/0, ∞/∞)
    - sequence: пределы последовательностей
    - special: замечательные пределы
    """
    return LimitsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 26. SetLogicTask - Множества и логика
##################################################

def generate_random_set_logic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> SetLogicTask:
    """
    Генерирует случайную задачу на множества и логику.
    
    Типы задач:
    - union: объединение множеств
    - intersection: пересечение
    - difference: разность
    - symmetric_difference: симметрическая разность
    - complement: дополнение
    - cardinality: мощность объединения
    - power_set: степень множества
    - cartesian_product: декартово произведение
    - boolean_simplify: упрощение логических выражений
    - truth_table: таблица истинности
    - venn_problem: задачи на диаграммы Венна
    """
    return SetLogicTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 18. Статистика
##################################################

def generate_random_statistics_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> StatisticsTask:
    """
    Генерирует случайную задачу по статистике.
    
    Типы задач:
    - mean: среднее арифметическое
    - median: медиана
    - mode: мода
    - variance: дисперсия
    - std_deviation: стандартное отклонение
    - correlation: корреляция Пирсона
    - linear_regression: линейная регрессия
    - percentile: перцентиль
    - quartiles: квартили
    - z_score: z-оценка
    """
    return StatisticsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 19. Интегралы
##################################################

def generate_random_integral_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> IntegralTask:
    """
    Генерирует случайную задачу на интегрирование.
    
    Типы задач:
    - indefinite_polynomial: неопределённый интеграл от многочлена
    - definite_polynomial: определённый интеграл от многочлена
    - indefinite_trig: неопределённый интеграл от тригонометрии
    - definite_trig: определённый интеграл от тригонометрии
    - area: площадь под кривой
    """
    return IntegralTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 20. Дифференциальные уравнения
##################################################

def generate_random_differential_equation_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> DifferentialEquationTask:
    """
    Генерирует случайную задачу на дифференциальные уравнения.
    
    Типы задач:
    - separable: с разделяющимися переменными
    - linear_first_order: линейные первого порядка
    - homogeneous_second_order: однородные второго порядка
    - exponential_growth: экспоненциальный рост
    - cauchy_problem: задача Коши
    """
    return DifferentialEquationTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 21. Оптимизация
##################################################

def generate_random_optimization_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> OptimizationTask:
    """
    Генерирует случайную задачу на оптимизацию.
    
    Типы задач:
    - find_extremum: поиск экстремумов
    - max_min_interval: max/min на отрезке
    - linear_programming: линейное программирование
    """
    return OptimizationTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 22. Векторы 3D
##################################################

def generate_random_vector_3d_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> Vector3DTask:
    """
    Генерирует случайную задачу по векторам в 3D.
    
    Типы задач:
    - cross_product: векторное произведение
    - triple_scalar: смешанное произведение
    - plane_equation: уравнение плоскости
    - distance_point_plane: расстояние от точки до плоскости
    - angle_vectors: угол между векторами
    - projection: проекция вектора
    - parallelpiped_volume: объём параллелепипеда
    """
    return Vector3DTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 23. Финансовая математика
##################################################

def generate_random_financial_math_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> FinancialMathTask:
    """
    Генерирует случайную задачу по финансовой математике.
    
    Типы задач:
    - simple_interest: простые проценты
    - compound_interest: сложные проценты
    - present_value: текущая стоимость
    - annuity_pv: текущая стоимость аннуитета
    - annuity_fv: будущая стоимость аннуитета
    - loan_payment: платёж по кредиту
    - npv: чистая приведённая стоимость
    """
    return FinancialMathTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 24. Ряды и сходимость
##################################################

def generate_random_series_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    task_type: str = None
,
    **kwargs
) -> SeriesTask:
    """
    Генерирует случайную задачу на ряды.
    
    Типы задач:
    - geometric_sum: сумма геометрического ряда
    - convergence_test: исследование сходимости
    - partial_sum: частичная сумма
    - telescoping: телескопический ряд
    """
    return SeriesTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 25. SudokuTask - Судоку
##################################################

def generate_random_sudoku_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    **kwargs
) -> SudokuTask:
    """Генерирует случайную задачу судоку."""
    return SudokuTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode
    )


##################################################
# 26. ZebraPuzzleTask - Загадка Эйнштейна
##################################################

def generate_random_zebra_puzzle_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    **kwargs
) -> ZebraPuzzleTask:
    """Генерирует случайную загадку Эйнштейна."""
    return ZebraPuzzleTask(
        language=language,
        detail_level=detail_level,
        difficulty=min(difficulty, 8),  # Ограничиваем для стабильности
        reasoning_mode=reasoning_mode
    )


##################################################
# 27. RiverCrossingTask - Задача о переправе
##################################################

def generate_random_river_crossing_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> RiverCrossingTask:
    """Генерирует случайную задачу о переправе."""
    return RiverCrossingTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 28. TowerOfHanoiTask - Ханойская башня
##################################################

def generate_random_tower_of_hanoi_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> TowerOfHanoiTask:
    """Генерирует случайную задачу Ханойской башни."""
    return TowerOfHanoiTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 29. WaterJugTask - Задача о кувшинах
##################################################

def generate_random_water_jug_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> WaterJugTask:
    """Генерирует случайную задачу о кувшинах."""
    return WaterJugTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 30. NimGameTask - Игра Ним
##################################################

def generate_random_nim_game_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
,
    **kwargs
) -> NimGameTask:
    """Генерирует случайную задачу игры Ним."""
    return NimGameTask(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# 31. LeanProofTask - Формальные доказательства
##################################################

def generate_random_lean_proof_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    category: str = None,
    **kwargs
) -> LeanProofTask:
    """
    Генерирует случайную задачу на формальное доказательство в Lean 4.
    
    Категории теорем:
    - propositional: пропозициональная логика (∧, ∨, →, ¬)
    - predicate: предикатная логика (∀, ∃)
    - nat_arithmetic: арифметика натуральных чисел
    - list: операции над списками
    - equality: свойства равенства
    
    Args:
        language: Язык ("ru" или "en")
        detail_level: Уровень детализации
        difficulty: Уровень сложности (1-10)
        category: Категория теоремы (если None — выбирается по сложности)
        
    Returns:
        LeanProofTask с теоремой и доказательством
    """
    return generate_lean_proof_task(
        difficulty=difficulty,
        language=language,
        category=category,
        detail_level=detail_level,
    )


##################################################
# 32. New reasoning families
##################################################

def generate_random_csp_reasoning_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> CSPReasoningTask:
    return CSPReasoningTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_sat_smt_mini_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> SATSMTMiniTask:
    return SATSMTMiniTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_proof_cases_counterexample_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> ProofCasesCounterexampleTask:
    return ProofCasesCounterexampleTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_graph_justification_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> GraphJustificationTask:
    return GraphJustificationTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_bayesian_reasoning_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> BayesianReasoningTask:
    return BayesianReasoningTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_combinatorial_optimization_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> CombinatorialOptimizationTask:
    return CombinatorialOptimizationTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def _mk_generator(task_cls):
    def _gen(language: str = "ru", detail_level: int = 3, difficulty: int = 5,
             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        return task_cls.generate_random_task(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs
        )
    return _gen


generate_random_cryptarithmetic_task = _mk_generator(CryptarithmeticTask)
generate_random_inequality_proof_task = _mk_generator(InequalityProofTask)
generate_random_symbolic_regression_task = _mk_generator(SymbolicRegressionTask)
generate_random_polynomial_factorization_task = _mk_generator(PolynomialFactorizationTask)
generate_random_base_conversion_task = _mk_generator(BaseConversionTask)
generate_random_modular_arithmetic_task = _mk_generator(ModularArithmeticTask)
generate_random_matrix_reasoning_task = _mk_generator(MatrixReasoningTask)

# Волна «важная математика»
generate_random_taylor_series_task = _mk_generator(TaylorSeriesTask)
generate_random_partial_fractions_task = _mk_generator(PartialFractionsTask)
generate_random_partial_derivatives_task = _mk_generator(PartialDerivativesTask)
generate_random_area_between_curves_task = _mk_generator(AreaBetweenCurvesTask)
generate_random_lhopital_task = _mk_generator(LHopitalTask)
generate_random_recurrence_task = _mk_generator(RecurrenceTask)
generate_random_prime_factorization_task = _mk_generator(PrimeFactorizationTask)
generate_random_diophantine_task = _mk_generator(DiophantineTask)
generate_random_modular_inverse_task = _mk_generator(ModularInverseTask)
generate_random_continued_fraction_task = _mk_generator(ContinuedFractionTask)
generate_random_generating_function_task = _mk_generator(GeneratingFunctionTask)
generate_random_gaussian_elimination_task = _mk_generator(GaussianEliminationTask)
generate_random_matrix_multiplication_task = _mk_generator(MatrixMultiplicationTask)
generate_random_gram_schmidt_task = _mk_generator(GramSchmidtTask)
generate_random_least_squares_task = _mk_generator(LeastSquaresTask)
generate_random_roots_of_unity_task = _mk_generator(RootsOfUnityTask)
generate_random_expected_value_task = _mk_generator(ExpectedValueTask)
generate_random_markov_chain_task = _mk_generator(MarkovChainTask)
generate_random_conditional_probability_task = _mk_generator(ConditionalProbabilityTask)
generate_random_hypothesis_testing_task = _mk_generator(HypothesisTestingTask)
generate_random_coordinate_geometry_task = _mk_generator(CoordinateGeometryTask)
generate_random_shoelace_area_task = _mk_generator(ShoelaceAreaTask)
generate_random_triangle_solving_task = _mk_generator(TriangleSolvingTask)
generate_random_conic_sections_task = _mk_generator(ConicSectionsTask)
generate_random_vieta_task = _mk_generator(VietaTask)

# Волна «ризонинг-задачи»
generate_random_graph_reasoning_task = _mk_generator(GraphReasoningTask)
generate_random_ordering_puzzle_task = _mk_generator(OrderingPuzzleTask)
generate_random_state_tracking_task = _mk_generator(StateTrackingTask)
generate_random_grid_navigation_task = _mk_generator(GridNavigationTask)
generate_random_interval_scheduling_task = _mk_generator(IntervalSchedulingTask)
generate_random_set_reasoning_task = _mk_generator(SetReasoningTask)
generate_random_pattern_induction_task = _mk_generator(PatternInductionTask)
generate_random_syllogism_task = _mk_generator(SyllogismTask)
generate_random_logical_entailment_task = _mk_generator(LogicalEntailmentTask)
generate_random_boolean_circuit_task = _mk_generator(BooleanCircuitTask)
generate_random_mastermind_task = _mk_generator(MastermindTask)
generate_random_countdown_24_task = _mk_generator(Countdown24Task)
generate_random_game_theory_optimal_task = _mk_generator(GameTheoryOptimalTask)
generate_random_family_tree_task = _mk_generator(FamilyTreeTask)
generate_random_minesweeper_deduction_task = _mk_generator(MinesweeperDeductionTask)
generate_random_n_queens_task = _mk_generator(NQueensTask)
generate_random_magic_square_task = _mk_generator(MagicSquareTask)
generate_random_skyscrapers_task = _mk_generator(SkyscrapersTask)
generate_random_kenken_task = _mk_generator(KenKenTask)
generate_random_kakuro_task = _mk_generator(KakuroTask)

generate_random_weighted_shortest_path_task = _mk_generator(WeightedShortestPathTask)
generate_random_topological_sort_task = _mk_generator(TopologicalSortTask)
generate_random_graph_coloring_task = _mk_generator(GraphColoringTask)
generate_random_mst_weight_task = _mk_generator(MSTWeightTask)
generate_random_eulerian_path_task = _mk_generator(EulerianPathTask)
generate_random_hamiltonian_path_task = _mk_generator(HamiltonianPathTask)
generate_random_bipartite_matching_task = _mk_generator(BipartiteMatchingTask)
generate_random_tsp_task = _mk_generator(TSPTask)
generate_random_max_flow_task = _mk_generator(MaxFlowTask)
generate_random_dag_longest_path_task = _mk_generator(DAGLongestPathTask)
generate_random_knapsack_task = _mk_generator(KnapsackTask)
generate_random_subset_sum_task = _mk_generator(SubsetSumTask)
generate_random_truth_table_task = _mk_generator(TruthTableTask)
generate_random_model_counting_task = _mk_generator(ModelCountingTask)
generate_random_three_sat_task = _mk_generator(ThreeSatTask)
generate_random_logical_equivalence_task = _mk_generator(LogicalEquivalenceTask)
generate_random_qbf_task = _mk_generator(QBFTask)
generate_random_dfa_simulation_task = _mk_generator(DFASimulationTask)
generate_random_turing_machine_task = _mk_generator(TuringMachineTask)
generate_random_game_of_life_task = _mk_generator(GameOfLifeTask)
generate_random_elementary_ca_task = _mk_generator(ElementaryCATask)
generate_random_rpn_eval_task = _mk_generator(RPNEvalTask)
generate_random_balanced_brackets_task = _mk_generator(BalancedBracketsTask)
generate_random_sorting_trace_task = _mk_generator(SortingTraceTask)
generate_random_nonogram_task = _mk_generator(NonogramTask)
generate_random_binary_puzzle_task = _mk_generator(BinaryPuzzleTask)
generate_random_hitori_task = _mk_generator(HitoriTask)
generate_random_star_battle_task = _mk_generator(StarBattleTask)
generate_random_battleship_task = _mk_generator(BattleshipTask)
generate_random_logic_grid_task = _mk_generator(LogicGridTask)
generate_random_seating_circular_task = _mk_generator(SeatingCircularTask)
generate_random_tournament_task = _mk_generator(TournamentTask)
generate_random_combinatorial_games_task = _mk_generator(CombinatorialGamesTask)
generate_random_tic_tac_toe_task = _mk_generator(TicTacToeTask)
generate_random_cube_net_task = _mk_generator(CubeNetTask)
generate_random_dice_reasoning_task = _mk_generator(DiceReasoningTask)
generate_random_rotation_reflection_task = _mk_generator(RotationReflectionTask)
generate_random_paper_folding_task = _mk_generator(PaperFoldingTask)
generate_random_cipher_decode_task = _mk_generator(CipherDecodeTask)
generate_random_pigeonhole_task = _mk_generator(PigeonholeTask)
generate_random_monty_hall_task = _mk_generator(MontyHallTask)
generate_random_allen_relations_task = _mk_generator(AllenRelationsTask)

generate_random_arc_grid_induction_task = _mk_generator(ARCGridInductionTask)
generate_random_program_trace_task = _mk_generator(ProgramTraceTask)
generate_random_sprague_grundy_task = _mk_generator(SpragueGrundyTask)
generate_random_natural_deduction_task = _mk_generator(NaturalDeductionTask)
generate_random_edit_distance_task = _mk_generator(EditDistanceTask)
generate_random_calendar_reasoning_task = _mk_generator(CalendarReasoningTask)
generate_random_word_ladder_task = _mk_generator(WordLadderTask)
generate_random_cfg_membership_task = _mk_generator(CFGMembershipTask)
generate_random_datalog_inference_task = _mk_generator(DatalogInferenceTask)
generate_random_unification_task = _mk_generator(UnificationTask)
generate_random_lambda_calculus_task = _mk_generator(LambdaCalculusTask)
generate_random_resolution_task = _mk_generator(ResolutionTask)
generate_random_lis_dp_task = _mk_generator(LISDPTask)
generate_random_kmp_matching_task = _mk_generator(KMPMatchingTask)
generate_random_sliding_puzzle_task = _mk_generator(SlidingPuzzleTask)
generate_random_algorithm_complexity_task = _mk_generator(AlgorithmComplexityTask)
generate_random_twos_complement_task = _mk_generator(TwosComplementTask)
generate_random_connect_four_task = _mk_generator(ConnectFourTask)
generate_random_graph_connectivity_task = _mk_generator(GraphConnectivityTask)
generate_random_huffman_coding_task = _mk_generator(HuffmanCodingTask)
generate_random_dfa_minimization_task = _mk_generator(DFAMinimizationTask)
generate_random_computational_geometry_task = _mk_generator(ComputationalGeometryTask)
generate_random_stable_matching_task = _mk_generator(StableMatchingTask)
generate_random_hamming_code_task = _mk_generator(HammingCodeTask)
generate_random_page_replacement_task = _mk_generator(PageReplacementTask)
generate_random_tree_queries_task = _mk_generator(TreeQueriesTask)
generate_random_os_scheduling_task = _mk_generator(OSSchedulingTask)
generate_random_numerical_methods_task = _mk_generator(NumericalMethodsTask)
generate_random_min_coins_task = _mk_generator(MinCoinsTask)
generate_random_lagrange_interpolation_task = _mk_generator(LagrangeInterpolationTask)
generate_random_euler_method_task = _mk_generator(EulerMethodTask)
generate_random_fractional_knapsack_task = _mk_generator(FractionalKnapsackTask)
generate_random_union_find_task = _mk_generator(UnionFindTask)
generate_random_direct_mapped_cache_task = _mk_generator(DirectMappedCacheTask)
generate_random_knight_moves_task = _mk_generator(KnightMovesTask)
generate_random_shannon_entropy_task = _mk_generator(ShannonEntropyTask)
generate_random_gini_split_task = _mk_generator(GiniSplitTask)
generate_random_knn_classify_task = _mk_generator(KNNClassifyTask)
generate_random_perceptron_update_task = _mk_generator(PerceptronUpdateTask)
generate_random_kmeans_step_task = _mk_generator(KMeansStepTask)
generate_random_naive_bayes_task = _mk_generator(NaiveBayesTask)
generate_random_confusion_metrics_task = _mk_generator(ConfusionMetricsTask)
generate_random_gradient_step_task = _mk_generator(GradientStepTask)
generate_random_ranking_auc_task = _mk_generator(RankingAUCTask)
generate_random_hinge_loss_task = _mk_generator(HingeLossTask)
generate_random_cosine_rank_task = _mk_generator(CosineRankTask)
generate_random_univariate_regression_task = _mk_generator(UnivariateRegressionTask)
generate_random_decision_stump_task = _mk_generator(DecisionStumpTask)
generate_random_brier_score_task = _mk_generator(BrierScoreTask)
generate_random_mse_loss_task = _mk_generator(MseTask)
generate_random_precision_at_k_task = _mk_generator(PrecisionAtKTask)
generate_random_cohen_kappa_task = _mk_generator(CohenKappaTask)
generate_random_r2_score_task = _mk_generator(R2Task)
generate_random_mean_average_precision_task = _mk_generator(AveragePrecisionTask)
generate_random_mae_loss_task = _mk_generator(MaeTask)
generate_random_jaccard_index_task = _mk_generator(JaccardTask)
generate_random_reciprocal_rank_task = _mk_generator(ReciprocalRankTask)
generate_random_kalman_update_task = _mk_generator(KalmanUpdateTask)
generate_random_hmm_decode_task = _mk_generator(HmmDecodeTask)
generate_random_elimination_query_task = _mk_generator(EliminationQueryTask)
generate_random_pagerank_task = _mk_generator(PageRankTask)
generate_random_catalan_task = _mk_generator(CatalanTask)
generate_random_stirling_second_task = _mk_generator(StirlingSecondTask)
generate_random_gray_code_task = _mk_generator(GrayCodeTask)
generate_random_binary_search_task = _mk_generator(BinarySearchTask)
generate_random_matrix_chain_task = _mk_generator(MatrixChainTask)
generate_random_common_substring_task = _mk_generator(CommonSubstringTask)
generate_random_solid_volume_task = _mk_generator(SolidVolumeTask)
generate_random_round_robin_task = _mk_generator(RoundRobinTask)
generate_random_deadlock_task = _mk_generator(DeadlockTask)
generate_random_second_price_task = _mk_generator(SecondPriceTask)
generate_random_shapley_value_task = _mk_generator(ShapleyValueTask)
generate_random_max_subarray_task = _mk_generator(MaxSubarrayTask)
generate_random_house_robber_task = _mk_generator(HouseRobberTask)
generate_random_rod_cutting_task = _mk_generator(RodCuttingTask)
generate_random_pair_sum_task = _mk_generator(PairSumTask)
generate_random_heap_array_task = _mk_generator(HeapTask)
generate_random_weighted_interval_task = _mk_generator(WeightedIntervalTask)
generate_random_discounted_return_task = _mk_generator(DiscountedReturnTask)
generate_random_q_learning_task = _mk_generator(QLearningTask)
generate_random_bellman_backup_task = _mk_generator(BellmanBackupTask)
generate_random_sarsa_task = _mk_generator(SarsaTask)
generate_random_epsilon_greedy_task = _mk_generator(EpsilonGreedyTask)
generate_random_policy_expectation_task = _mk_generator(PolicyExpectationTask)
generate_random_reward_to_go_task = _mk_generator(RewardToGoTask)
generate_random_double_q_task = _mk_generator(DoubleQTask)
generate_random_polyak_update_task = _mk_generator(PolyakTask)
generate_random_eligibility_trace_task = _mk_generator(EligibilityTraceTask)
generate_random_expected_sarsa_task = _mk_generator(ExpectedSarsaTask)
generate_random_gae_advantage_task = _mk_generator(GaeTask)
generate_random_ppo_clip_task = _mk_generator(PpoClipTask)
generate_random_importance_ratio_task = _mk_generator(ImportanceRatioTask)
generate_random_average_reward_task = _mk_generator(AverageRewardTask)
generate_random_vtrace_task = _mk_generator(VTraceTask)
generate_random_priority_replay_task = _mk_generator(PriorityReplayTask)
generate_random_reward_clip_task = _mk_generator(RewardClipTask)
generate_random_finite_horizon_task = _mk_generator(FiniteHorizonTask)
generate_random_q_trajectory_task = _mk_generator(QTrajectoryTask)
generate_random_sarsa_trajectory_task = _mk_generator(SarsaTrajectoryTask)
generate_random_double_q_trajectory_task = _mk_generator(DoubleQTrajectoryTask)
generate_random_min_path_sum_task = _mk_generator(MinPathSumTask)
generate_random_stock_profit_task = _mk_generator(StockProfitTask)
generate_random_jump_game_task = _mk_generator(JumpGameTask)
generate_random_container_water_task = _mk_generator(ContainerWaterTask)
generate_random_decode_ways_task = _mk_generator(DecodeWaysTask)
generate_random_gas_station_task = _mk_generator(GasStationTask)
generate_random_dag_paths_task = _mk_generator(DagPathsTask)
generate_random_shortest_path_count_task = _mk_generator(ShortestCountTask)
generate_random_triangle_girth_task = _mk_generator(TriangleGirthTask)
generate_random_wiener_index_task = _mk_generator(WienerTask)
generate_random_tree_radius_task = _mk_generator(TreeRadiusTask)
generate_random_prufer_code_task = _mk_generator(PruferTask)
generate_random_havel_hakimi_task = _mk_generator(HavelHakimiTask)
generate_random_spanning_trees_task = _mk_generator(SpanningTreesTask)
generate_random_topo_count_task = _mk_generator(TopoCountTask)
generate_random_pick_theorem_task = _mk_generator(PickTheoremTask)
generate_random_trapping_rain_task = _mk_generator(TrappingRainTask)
generate_random_majority_element_task = _mk_generator(MajorityTask)
generate_random_euclid_gcd_task = _mk_generator(EuclidTask)
generate_random_josephus_task = _mk_generator(JosephusTask)
generate_random_collatz_steps_task = _mk_generator(CollatzTask)
generate_random_histogram_area_task = _mk_generator(HistogramTask)
generate_random_target_sum_task = _mk_generator(TargetSumTask)
generate_random_stock_unlimited_task = _mk_generator(StockUnlimitedTask)
generate_random_min_squares_task = _mk_generator(MinSquaresTask)
generate_random_palindrome_subseq_task = _mk_generator(PalindromeSubseqTask)
generate_random_subarray_sum_task = _mk_generator(SubarraySumTask)
generate_random_integer_sqrt_task = _mk_generator(IntegerSqrtTask)
generate_random_max_product_task = _mk_generator(MaxProductTask)
generate_random_min_assignment_task = _mk_generator(MinAssignmentTask)
generate_random_floyd_distance_task = _mk_generator(FloydDistanceTask)
generate_random_sequence_alignment_task = _mk_generator(SequenceAlignmentTask)
generate_random_range_query_task = _mk_generator(RangeQueryTask)
generate_random_mixed_nash_task = _mk_generator(MixedNashTask)
generate_random_expectimax_task = _mk_generator(ExpectimaxTask)
generate_random_minimax_tree_task = _mk_generator(MinimaxTreeTask)
generate_random_local_alignment_task = _mk_generator(LocalAlignmentTask)
generate_random_nussinov_task = _mk_generator(NussinovTask)
generate_random_optimal_bst_task = _mk_generator(OptimalBstTask)
generate_random_alpha_beta_task = _mk_generator(AlphaBetaTask)
generate_random_polynomial_product_task = _mk_generator(PolynomialProductTask)
generate_random_range_add_task = _mk_generator(RangeAddTask)
generate_random_tree_mis_task = _mk_generator(TreeMisTask)
generate_random_subsequence_count_task = _mk_generator(SubsequenceCountTask)
generate_random_secret_share_task = _mk_generator(SecretShareTask)


def generate_random_regex_dfa_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> RegexDFATask:
    return RegexDFATask.generate_random_task(
        language=language, detail_level=detail_level, difficulty=difficulty,
        reasoning_mode=reasoning_mode, augment=augment, **kwargs
    )


def generate_random_dynamic_programming_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> DynamicProgrammingTask:
    return DynamicProgrammingTask.generate_random_task(
        language=language, detail_level=detail_level, difficulty=difficulty,
        reasoning_mode=reasoning_mode, augment=augment, **kwargs
    )


def generate_random_blocks_world_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> BlocksWorldTask:
    return BlocksWorldTask.generate_random_task(
        language=language, detail_level=detail_level, difficulty=difficulty,
        reasoning_mode=reasoning_mode, augment=augment, **kwargs
    )


def generate_random_find_the_error_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> FindTheErrorTask:
    return FindTheErrorTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_propositional_logic_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> PropositionalLogicTask:
    return PropositionalLogicTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


def generate_random_symbolic_simplification_task(
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    reasoning_mode: bool = False,
    augment: bool = True,
    **kwargs
) -> SymbolicSimplificationTask:
    return SymbolicSimplificationTask.generate_random_task(
        language=language,
        detail_level=detail_level,
        difficulty=difficulty,
        reasoning_mode=reasoning_mode,
        augment=augment,
        **kwargs
    )


##################################################
# Универсальный генератор всех типов задач
##################################################

ALL_TASK_GENERATORS = {
    "arithmetic": generate_random_arithmetic_task,
    "linear": generate_random_linear_task,
    "quadratic": generate_random_quadratic_task,
    "cubic": generate_random_cubic_task,
    "exponential": generate_random_exponential_task,
    "logarithmic": generate_random_logarithmic_task,
    "calculus": generate_random_calculus_task,
    "contradiction": generate_random_contradiction_task,
    "knights_knaves": generate_random_knights_knaves_task,
    "futoshiki": generate_random_futoshiki_task,
    "urn_probability": generate_random_urn_probability_task,
    "text_stats": generate_random_text_stats_task,
    "graph": generate_random_graph_task,
    "system_linear": generate_random_system_linear_task,
    "analogical": generate_random_analogical_task,
    "group_theory": generate_random_group_theory_task,
    "category_theory": generate_random_category_theory_task,
    # Новые задачи:
    "number_theory": generate_random_number_theory_task,
    "combinatorics": generate_random_combinatorics_task,
    "sequence": generate_random_sequence_task,
    "geometry": generate_random_geometry_task,
    "matrix": generate_random_matrix_task,
    "trigonometry": generate_random_trigonometry_task,
    "inequality": generate_random_inequality_task,
    "symbolic_simplification": generate_random_symbolic_simplification_task,
    "complex_number": generate_random_complex_number_task,
    "limits": generate_random_limits_task,
    "set_logic": generate_random_set_logic_task,
    # Новые задачи (вторая волна):
    "statistics": generate_random_statistics_task,
    "integral": generate_random_integral_task,
    "differential_equation": generate_random_differential_equation_task,
    "optimization": generate_random_optimization_task,
    "vector_3d": generate_random_vector_3d_task,
    "financial_math": generate_random_financial_math_task,
    "series": generate_random_series_task,
    # Новые reasoning задачи:
    "sudoku": generate_random_sudoku_task,
    "zebra_puzzle": generate_random_zebra_puzzle_task,
    "river_crossing": generate_random_river_crossing_task,
    "tower_of_hanoi": generate_random_tower_of_hanoi_task,
    "water_jug": generate_random_water_jug_task,
    "nim_game": generate_random_nim_game_task,
    "csp_reasoning": generate_random_csp_reasoning_task,
    "sat_smt_mini": generate_random_sat_smt_mini_task,
    "proof_cases_counterexample": generate_random_proof_cases_counterexample_task,
    "find_the_error": generate_random_find_the_error_task,
    "propositional_logic": generate_random_propositional_logic_task,
    "regex_dfa": generate_random_regex_dfa_task,
    "dynamic_programming": generate_random_dynamic_programming_task,
    "blocks_world": generate_random_blocks_world_task,
    "cryptarithmetic": generate_random_cryptarithmetic_task,
    "inequality_proof": generate_random_inequality_proof_task,
    "symbolic_regression": generate_random_symbolic_regression_task,
    "polynomial_factorization": generate_random_polynomial_factorization_task,
    "base_conversion": generate_random_base_conversion_task,
    "modular_arithmetic": generate_random_modular_arithmetic_task,
    "matrix_reasoning": generate_random_matrix_reasoning_task,
    # Волна «важная математика»:
    "taylor_series": generate_random_taylor_series_task,
    "partial_fractions": generate_random_partial_fractions_task,
    "partial_derivatives": generate_random_partial_derivatives_task,
    "area_between_curves": generate_random_area_between_curves_task,
    "lhopital": generate_random_lhopital_task,
    "recurrence": generate_random_recurrence_task,
    "prime_factorization": generate_random_prime_factorization_task,
    "diophantine": generate_random_diophantine_task,
    "modular_inverse": generate_random_modular_inverse_task,
    "continued_fraction": generate_random_continued_fraction_task,
    "generating_function": generate_random_generating_function_task,
    "gaussian_elimination": generate_random_gaussian_elimination_task,
    "matrix_multiplication": generate_random_matrix_multiplication_task,
    "gram_schmidt": generate_random_gram_schmidt_task,
    "least_squares": generate_random_least_squares_task,
    "roots_of_unity": generate_random_roots_of_unity_task,
    "expected_value": generate_random_expected_value_task,
    "markov_chain": generate_random_markov_chain_task,
    "conditional_probability": generate_random_conditional_probability_task,
    "hypothesis_testing": generate_random_hypothesis_testing_task,
    "coordinate_geometry": generate_random_coordinate_geometry_task,
    "shoelace_area": generate_random_shoelace_area_task,
    "triangle_solving": generate_random_triangle_solving_task,
    "conic_sections": generate_random_conic_sections_task,
    "vieta": generate_random_vieta_task,
    # Волна «ризонинг-задачи»:
    "graph_reasoning": generate_random_graph_reasoning_task,
    "ordering_puzzle": generate_random_ordering_puzzle_task,
    "state_tracking": generate_random_state_tracking_task,
    "grid_navigation": generate_random_grid_navigation_task,
    "interval_scheduling": generate_random_interval_scheduling_task,
    "set_reasoning": generate_random_set_reasoning_task,
    "pattern_induction": generate_random_pattern_induction_task,
    "syllogism": generate_random_syllogism_task,
    "logical_entailment": generate_random_logical_entailment_task,
    "boolean_circuit": generate_random_boolean_circuit_task,
    "mastermind": generate_random_mastermind_task,
    "countdown_24": generate_random_countdown_24_task,
    "game_theory_optimal": generate_random_game_theory_optimal_task,
    "family_tree": generate_random_family_tree_task,
    "minesweeper_deduction": generate_random_minesweeper_deduction_task,
    "n_queens": generate_random_n_queens_task,
    "magic_square": generate_random_magic_square_task,
    "skyscrapers": generate_random_skyscrapers_task,
    "kenken": generate_random_kenken_task,
    "kakuro": generate_random_kakuro_task,
    # Волна «графы / оптимизация / симуляция / сетки / дедукция / игры / пространство»:
    "weighted_shortest_path": generate_random_weighted_shortest_path_task,
    "topological_sort": generate_random_topological_sort_task,
    "graph_coloring": generate_random_graph_coloring_task,
    "mst_weight": generate_random_mst_weight_task,
    "eulerian_path": generate_random_eulerian_path_task,
    "hamiltonian_path": generate_random_hamiltonian_path_task,
    "bipartite_matching": generate_random_bipartite_matching_task,
    "tsp": generate_random_tsp_task,
    "max_flow": generate_random_max_flow_task,
    "dag_longest_path": generate_random_dag_longest_path_task,
    "knapsack": generate_random_knapsack_task,
    "subset_sum": generate_random_subset_sum_task,
    "truth_table": generate_random_truth_table_task,
    "model_counting": generate_random_model_counting_task,
    "three_sat": generate_random_three_sat_task,
    "logical_equivalence": generate_random_logical_equivalence_task,
    "qbf": generate_random_qbf_task,
    "dfa_simulation": generate_random_dfa_simulation_task,
    "turing_machine": generate_random_turing_machine_task,
    "game_of_life": generate_random_game_of_life_task,
    "elementary_ca": generate_random_elementary_ca_task,
    "rpn_eval": generate_random_rpn_eval_task,
    "balanced_brackets": generate_random_balanced_brackets_task,
    "sorting_trace": generate_random_sorting_trace_task,
    "nonogram": generate_random_nonogram_task,
    "binary_puzzle": generate_random_binary_puzzle_task,
    "hitori": generate_random_hitori_task,
    "star_battle": generate_random_star_battle_task,
    "battleship": generate_random_battleship_task,
    "logic_grid": generate_random_logic_grid_task,
    "seating_circular": generate_random_seating_circular_task,
    "tournament": generate_random_tournament_task,
    "combinatorial_games": generate_random_combinatorial_games_task,
    "tic_tac_toe": generate_random_tic_tac_toe_task,
    "cube_net": generate_random_cube_net_task,
    "dice_reasoning": generate_random_dice_reasoning_task,
    "rotation_reflection": generate_random_rotation_reflection_task,
    "paper_folding": generate_random_paper_folding_task,
    "cipher_decode": generate_random_cipher_decode_task,
    "pigeonhole": generate_random_pigeonhole_task,
    "monty_hall": generate_random_monty_hall_task,
    "allen_relations": generate_random_allen_relations_task,
    # Волна «продвинутый ризонинг»:
    "arc_grid_induction": generate_random_arc_grid_induction_task,
    "program_trace": generate_random_program_trace_task,
    "sprague_grundy": generate_random_sprague_grundy_task,
    "natural_deduction": generate_random_natural_deduction_task,
    "edit_distance": generate_random_edit_distance_task,
    "calendar_reasoning": generate_random_calendar_reasoning_task,
    "word_ladder": generate_random_word_ladder_task,
    "cfg_membership": generate_random_cfg_membership_task,
    "datalog_inference": generate_random_datalog_inference_task,
    "unification": generate_random_unification_task,
    "lambda_calculus": generate_random_lambda_calculus_task,
    "resolution": generate_random_resolution_task,
    "lis_dp": generate_random_lis_dp_task,
    "kmp_matching": generate_random_kmp_matching_task,
    "sliding_puzzle": generate_random_sliding_puzzle_task,
    "algorithm_complexity": generate_random_algorithm_complexity_task,
    "twos_complement": generate_random_twos_complement_task,
    "connect_four": generate_random_connect_four_task,
    "graph_connectivity": generate_random_graph_connectivity_task,
    "huffman_coding": generate_random_huffman_coding_task,
    "dfa_minimization": generate_random_dfa_minimization_task,
    "computational_geometry": generate_random_computational_geometry_task,
    "stable_matching": generate_random_stable_matching_task,
    "hamming_code": generate_random_hamming_code_task,
    "page_replacement": generate_random_page_replacement_task,
    "tree_queries": generate_random_tree_queries_task,
    "os_scheduling": generate_random_os_scheduling_task,
    "numerical_methods": generate_random_numerical_methods_task,
    "min_coins": generate_random_min_coins_task,
    "lagrange_interpolation": generate_random_lagrange_interpolation_task,
    "euler_method": generate_random_euler_method_task,
    "fractional_knapsack": generate_random_fractional_knapsack_task,
    "union_find": generate_random_union_find_task,
    "direct_mapped_cache": generate_random_direct_mapped_cache_task,
    "knight_moves": generate_random_knight_moves_task,
    "shannon_entropy": generate_random_shannon_entropy_task,
    "gini_split": generate_random_gini_split_task,
    "knn_classify": generate_random_knn_classify_task,
    "perceptron_update": generate_random_perceptron_update_task,
    "kmeans_step": generate_random_kmeans_step_task,
    "naive_bayes": generate_random_naive_bayes_task,
    "confusion_metrics": generate_random_confusion_metrics_task,
    "gradient_step": generate_random_gradient_step_task,
    "ranking_auc": generate_random_ranking_auc_task,
    "hinge_loss": generate_random_hinge_loss_task,
    "cosine_rank": generate_random_cosine_rank_task,
    "univariate_regression": generate_random_univariate_regression_task,
    "decision_stump": generate_random_decision_stump_task,
    "brier_score": generate_random_brier_score_task,
    "mse_loss": generate_random_mse_loss_task,
    "precision_at_k": generate_random_precision_at_k_task,
    "cohen_kappa": generate_random_cohen_kappa_task,
    "r2_score": generate_random_r2_score_task,
    "mean_average_precision": generate_random_mean_average_precision_task,
    "mae_loss": generate_random_mae_loss_task,
    "jaccard_index": generate_random_jaccard_index_task,
    "reciprocal_rank": generate_random_reciprocal_rank_task,
    "kalman_update": generate_random_kalman_update_task,
    "hmm_decode": generate_random_hmm_decode_task,
    "elimination_query": generate_random_elimination_query_task,
    "pagerank": generate_random_pagerank_task,
    "catalan": generate_random_catalan_task,
    "stirling_second": generate_random_stirling_second_task,
    "gray_code": generate_random_gray_code_task,
    "binary_search": generate_random_binary_search_task,
    "matrix_chain": generate_random_matrix_chain_task,
    "common_substring": generate_random_common_substring_task,
    "solid_volume": generate_random_solid_volume_task,
    "round_robin": generate_random_round_robin_task,
    "deadlock": generate_random_deadlock_task,
    "second_price": generate_random_second_price_task,
    "shapley_value": generate_random_shapley_value_task,
    "max_subarray": generate_random_max_subarray_task,
    "house_robber": generate_random_house_robber_task,
    "rod_cutting": generate_random_rod_cutting_task,
    "pair_sum": generate_random_pair_sum_task,
    "heap_array": generate_random_heap_array_task,
    "weighted_interval": generate_random_weighted_interval_task,
    "discounted_return": generate_random_discounted_return_task,
    "q_learning": generate_random_q_learning_task,
    "bellman_backup": generate_random_bellman_backup_task,
    "sarsa": generate_random_sarsa_task,
    "epsilon_greedy": generate_random_epsilon_greedy_task,
    "policy_expectation": generate_random_policy_expectation_task,
    "reward_to_go": generate_random_reward_to_go_task,
    "double_q": generate_random_double_q_task,
    "polyak_update": generate_random_polyak_update_task,
    "eligibility_trace": generate_random_eligibility_trace_task,
    "expected_sarsa": generate_random_expected_sarsa_task,
    "gae_advantage": generate_random_gae_advantage_task,
    "ppo_clip": generate_random_ppo_clip_task,
    "importance_ratio": generate_random_importance_ratio_task,
    "average_reward": generate_random_average_reward_task,
    "vtrace": generate_random_vtrace_task,
    "priority_replay": generate_random_priority_replay_task,
    "reward_clip": generate_random_reward_clip_task,
    "finite_horizon": generate_random_finite_horizon_task,
    "q_trajectory": generate_random_q_trajectory_task,
    "sarsa_trajectory": generate_random_sarsa_trajectory_task,
    "double_q_trajectory": generate_random_double_q_trajectory_task,
    "min_path_sum": generate_random_min_path_sum_task,
    "stock_profit": generate_random_stock_profit_task,
    "jump_game": generate_random_jump_game_task,
    "container_water": generate_random_container_water_task,
    "decode_ways": generate_random_decode_ways_task,
    "gas_station": generate_random_gas_station_task,
    "dag_paths": generate_random_dag_paths_task,
    "shortest_path_count": generate_random_shortest_path_count_task,
    "triangle_girth": generate_random_triangle_girth_task,
    "wiener_index": generate_random_wiener_index_task,
    "tree_radius": generate_random_tree_radius_task,
    "prufer_code": generate_random_prufer_code_task,
    "havel_hakimi": generate_random_havel_hakimi_task,
    "spanning_trees": generate_random_spanning_trees_task,
    "topo_count": generate_random_topo_count_task,
    "pick_theorem": generate_random_pick_theorem_task,
    "trapping_rain": generate_random_trapping_rain_task,
    "majority_element": generate_random_majority_element_task,
    "euclid_gcd": generate_random_euclid_gcd_task,
    "josephus": generate_random_josephus_task,
    "collatz_steps": generate_random_collatz_steps_task,
    "histogram_area": generate_random_histogram_area_task,
    "target_sum": generate_random_target_sum_task,
    "stock_unlimited": generate_random_stock_unlimited_task,
    "min_squares": generate_random_min_squares_task,
    "palindrome_subseq": generate_random_palindrome_subseq_task,
    "subarray_sum": generate_random_subarray_sum_task,
    "integer_sqrt": generate_random_integer_sqrt_task,
    "max_product": generate_random_max_product_task,
    "min_assignment": generate_random_min_assignment_task,
    "floyd_distance": generate_random_floyd_distance_task,
    "sequence_alignment": generate_random_sequence_alignment_task,
    "range_query": generate_random_range_query_task,
    "mixed_nash": generate_random_mixed_nash_task,
    "expectimax": generate_random_expectimax_task,
    "minimax_tree": generate_random_minimax_tree_task,
    "local_alignment": generate_random_local_alignment_task,
    "nussinov": generate_random_nussinov_task,
    "optimal_bst": generate_random_optimal_bst_task,
    "alpha_beta": generate_random_alpha_beta_task,
    "polynomial_product": generate_random_polynomial_product_task,
    "range_add": generate_random_range_add_task,
    "tree_mis": generate_random_tree_mis_task,
    "subsequence_count": generate_random_subsequence_count_task,
    "secret_share": generate_random_secret_share_task,
    "graph_justification": generate_random_graph_justification_task,
    "bayesian_reasoning": generate_random_bayesian_reasoning_task,
    "combinatorial_optimization": generate_random_combinatorial_optimization_task,
    # Формальная математика (Lean 4):
    "lean_proof": generate_random_lean_proof_task,
    # Физические задачи (добавляем все из physics):
    **ALL_PHYSICS_TASK_GENERATORS,
}


def generate_random_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5,
    seed: Optional[int] = None,
    **kwargs
):
    """
    Универсальный генератор случайной задачи.
    
    Если task_type не указан, выбирается случайный тип.
    
    :param task_type: тип задачи (см. ALL_TASK_GENERATORS.keys())
    :param language: 'ru' или 'en'
    :param detail_level: уровень детализации решения
    :param difficulty: уровень сложности (1-10)
    :param seed: если задан — фиксирует random/numpy для воспроизводимости
    :param kwargs: дополнительные параметры для конкретного генератора
    :return: экземпляр задачи
    """
    if seed is not None:
        random.seed(seed)
        try:
            import numpy as _np
            _np.random.seed(seed % (2 ** 32))
        except Exception:
            pass

    if task_type is None:
        task_type = random.choice(list(ALL_TASK_GENERATORS.keys()))
    
    generator = ALL_TASK_GENERATORS.get(task_type)
    if generator is None:
        raise ValueError(f"Неизвестный тип задачи: {task_type}. Доступные: {list(ALL_TASK_GENERATORS.keys())}")
    
    # Передаём параметры, которые поддерживает генератор
    return generator(language=language, detail_level=detail_level, difficulty=difficulty, **kwargs)
