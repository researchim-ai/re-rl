from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'generators_i18n.json')

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
from re_rl.tasks.math.probability.dice_ways_task import DiceWaysTask
from re_rl.tasks.math.applied.map_scale_task import MapScaleTask
from re_rl.tasks.math.applied.age_gap_task import AgeGapTask
from re_rl.tasks.math.applied.crew_work_task import CrewWorkTask
from re_rl.tasks.math.applied.mix_chain_task import MixChainTask

# Прикладная математика
from re_rl.tasks.math.applied.financial_math_task import FinancialMathTask
from re_rl.tasks.math.applied.arithmetic_task import ArithmeticTask
from re_rl.tasks.math.applied.work_rates_task import WorkRatesTask
from re_rl.tasks.math.applied.mixture_concentration_task import MixtureConcentrationTask
from re_rl.tasks.math.applied.ratio_split_task import RatioSplitTask

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
from re_rl.tasks.math.geometry.clock_hands_task import ClockHandsTask
from re_rl.tasks.math.geometry.polygon_angles_task import PolygonAnglesTask
from re_rl.tasks.math.geometry.grid_diagonal_task import GridDiagonalTask
from re_rl.tasks.math.geometry.triangle_sides_task import TriangleSidesTask
from re_rl.tasks.math.discrete.divisor_sum_task import DivisorSumTask
from re_rl.tasks.math.discrete.digital_root_task import DigitalRootTask
from re_rl.tasks.math.discrete.frobenius_coin_task import FrobeniusCoinTask
from re_rl.tasks.math.discrete.bit_count_task import BitCountTask
from re_rl.tasks.math.discrete.odd_sum_task import OddSumTask
from re_rl.tasks.math.discrete.mod_chain_task import ModChainTask
from re_rl.tasks.math.discrete.gcd_chain_task import GcdChainTask
from re_rl.tasks.math.discrete.recurrence_walk_task import RecurrenceWalkTask
from re_rl.tasks.math.logic.turtle_walk_task import TurtleWalkTask
from re_rl.tasks.math.logic.portal_walk_task import PortalWalkTask
from re_rl.tasks.math.algebra.horner_eval_task import HornerEvalTask
from re_rl.tasks.math.applied.ledger_guard_task import LedgerGuardTask
from re_rl.tasks.math.applied.truck_trips_task import TruckTripsTask
from re_rl.tasks.math.discrete.door_toggles_task import DoorTogglesTask
from re_rl.tasks.math.discrete.greedy_coins_task import GreedyCoinsTask
from re_rl.tasks.math.discrete.walk_range_task import WalkRangeTask
from re_rl.tasks.math.discrete.carry_add_task import CarryAddTask
from re_rl.tasks.math.logic.line_infection_task import LineInfectionTask
from re_rl.tasks.math.logic.corridor_keys_task import CorridorKeysTask
from re_rl.tasks.math.logic.next_greater_task import NextGreaterTask
from re_rl.tasks.math.logic.window_max_task import WindowMaxTask
from re_rl.tasks.math.logic.two_pointer_merge_task import TwoPointerMergeTask
from re_rl.tasks.math.logic.cooldown_schedule_task import CooldownScheduleTask
from re_rl.tasks.math.logic.pancake_trace_task import PancakeTraceTask
from re_rl.tasks.math.logic.bracket_scan_task import BracketScanTask
from re_rl.tasks.ml.kmeans_rounds_task import KMeansRoundsTask
from re_rl.tasks.math.probability.bayes_updates_task import BayesUpdatesTask
from re_rl.tasks.math.probability.polya_urn_task import PolyaUrnTask
from re_rl.tasks.rl.policy_rollout_task import PolicyRolloutTask
from re_rl.tasks.ml.boost_weights_task import BoostWeightsTask
from re_rl.tasks.ml.momentum_sgd_task import MomentumSgdTask
from re_rl.tasks.ml.decision_list_task import DecisionListTask
from re_rl.tasks.rl.td_table_task import TdTableTask
from re_rl.tasks.math.discrete.extended_euclid_task import ExtendedEuclidTask
from re_rl.tasks.math.discrete.crt_chain_task import CrtChainTask
from re_rl.tasks.math.discrete.cf_expand_task import CfExpandTask
from re_rl.tasks.math.discrete.nim_sum_task import NimSumTask
from re_rl.tasks.math.analysis.difference_table_task import DifferenceTableTask
from re_rl.tasks.math.discrete.sandpile_path_task import SandpilePathTask
from re_rl.tasks.math.probability.markov_steps_task import MarkovStepsTask
from re_rl.tasks.math.probability.sir_ticks_task import SirTicksTask
from re_rl.tasks.math.algebra.poly_div_task import PolyDivTask
from re_rl.tasks.math.logic.johnson_span_task import JohnsonSpanTask
from re_rl.tasks.math.logic.lights_path_task import LightsPathTask
from re_rl.tasks.math.logic.domino_chain_task import DominoChainTask
from re_rl.tasks.math.logic.bound_scan_task import BoundScanTask
from re_rl.tasks.math.logic.claim_count_task import ClaimCountTask
from re_rl.tasks.math.logic.quorum_rise_task import QuorumRiseTask
from re_rl.tasks.math.logic.hat_line_task import HatLineTask
from re_rl.tasks.math.logic.reagent_chain_task import ReagentChainTask
from re_rl.tasks.math.logic.tax_brackets_task import TaxBracketsTask
from re_rl.tasks.math.logic.codon_scan_task import CodonScanTask
from re_rl.tasks.math.logic.dose_schedule_task import DoseScheduleTask
from re_rl.tasks.math.logic.melody_walk_task import MelodyWalkTask
from re_rl.tasks.math.logic.fifo_cost_task import FifoCostTask
from re_rl.tasks.math.logic.borda_count_task import BordaCountTask
from re_rl.tasks.math.logic.shift_add_task import ShiftAddTask
from re_rl.tasks.math.logic.rally_lead_task import RallyLeadTask
from re_rl.tasks.math.discrete.pascal_row_task import PascalRowTask
from re_rl.tasks.math.algebra.fraction_ops_task import FractionOpsTask
from re_rl.tasks.math.discrete.stern_path_task import SternPathTask
from re_rl.tasks.math.discrete.partition_count_task import PartitionCountTask
from re_rl.tasks.math.discrete.derange_count_task import DerangeCountTask
from re_rl.tasks.math.algebra.gauss_mul_task import GaussMulTask
from re_rl.tasks.math.discrete.perm_compose_task import PermComposeTask
from re_rl.tasks.math.geometry.cover_span_task import CoverSpanTask
from re_rl.tasks.math.discrete.reverse_add_task import ReverseAddTask
from re_rl.tasks.math.probability.stream_median_task import StreamMedianTask
from re_rl.tasks.math.discrete.totient_row_task import TotientRowTask
from re_rl.tasks.math.discrete.coprime_count_task import CoprimeCountTask
from re_rl.tasks.math.algebra.digit_div_task import DigitDivTask
from re_rl.tasks.math.discrete.tree_depth_task import TreeDepthTask
from re_rl.tasks.math.discrete.sign_walk_task import SignWalkTask
from re_rl.tasks.math.discrete.perm_rank_task import PermRankTask
from re_rl.tasks.math.discrete.lcm_rise_task import LcmRiseTask
from re_rl.tasks.math.discrete.zigzag_row_task import ZigzagRowTask
from re_rl.tasks.math.discrete.record_highs_task import RecordHighsTask
from re_rl.tasks.math.discrete.sum_kinds_task import SumKindsTask
from re_rl.tasks.math.discrete.fib_word_task import FibWordTask
from re_rl.tasks.math.probability.mode_track_task import ModeTrackTask
from re_rl.tasks.math.discrete.look_say_task import LookSayTask
from re_rl.tasks.math.discrete.zeckendorf_task import ZeckendorfTask
from re_rl.tasks.math.discrete.roman_value_task import RomanValueTask
from re_rl.tasks.math.discrete.digit_stream_task import DigitStreamTask
from re_rl.tasks.math.logic.deque_trace_task import DequeTraceTask
from re_rl.tasks.math.discrete.dragon_fold_task import DragonFoldTask
from re_rl.tasks.math.discrete.permanent_task import PermanentTask
from re_rl.tasks.math.discrete.bead_count_task import BeadCountTask
from re_rl.tasks.math.discrete.negabase_task import NegabaseTask
from re_rl.tasks.math.geometry.ulam_walk_task import UlamWalkTask
from re_rl.tasks.math.discrete.luhn_sum_task import LuhnSumTask
from re_rl.tasks.math.discrete.kaprekar_step_task import KaprekarStepTask
from re_rl.tasks.math.discrete.morton_code_task import MortonCodeTask
from re_rl.tasks.math.logic.stock_span_task import StockSpanTask
from re_rl.tasks.math.logic.candy_row_task import CandyRowTask
from re_rl.tasks.math.discrete.digit_fact_task import DigitFactTask
from re_rl.tasks.math.discrete.recaman_task import RecamanTask
from re_rl.tasks.math.discrete.xor_basis_task import XorBasisTask
from re_rl.tasks.math.discrete.palindrome_radius_task import PalindromeRadiusTask
from re_rl.tasks.math.discrete.squarefree_row_task import SquarefreeRowTask
from re_rl.tasks.math.logic.fenwick_sum_task import FenwickSumTask
from re_rl.tasks.math.logic.sparse_min_task import SparseMinTask
from re_rl.tasks.math.logic.z_array_task import ZArrayTask
from re_rl.tasks.math.logic.selection_swaps_task import SelectionSwapsTask
from re_rl.tasks.math.logic.rho_cycle_task import RhoCycleTask
from re_rl.tasks.math.logic.tree_times_task import TreeTimesTask
from re_rl.tasks.math.logic.dutch_flag_task import DutchFlagTask
from re_rl.tasks.math.logic.window_distinct_task import WindowDistinctTask
from re_rl.tasks.math.logic.stable_place_task import StablePlaceTask
from re_rl.tasks.math.logic.naive_find_task import NaiveFindTask
from re_rl.tasks.math.logic.budget_take_task import BudgetTakeTask
from re_rl.tasks.math.logic.skip_op_task import SkipOpTask
from re_rl.tasks.math.logic.retry_goal_task import RetryGoalTask
from re_rl.tasks.math.logic.signal_edges_task import SignalEdgesTask
from re_rl.tasks.math.logic.plan_gate_task import PlanGateTask
from re_rl.tasks.math.logic.tool_pick_task import ToolPickTask
from re_rl.tasks.math.logic.diff_count_task import DiffCountTask
from re_rl.tasks.math.logic.cell_patch_task import CellPatchTask
from re_rl.tasks.math.logic.pred_scan_task import PredScanTask
from re_rl.tasks.math.logic.rate_limit_task import RateLimitTask
from re_rl.tasks.math.logic.lateness_task import LatenessTask
from re_rl.tasks.math.logic.switch_flip_task import SwitchFlipTask
from re_rl.tasks.math.geometry.turn_signs_task import TurnSignsTask
from re_rl.tasks.math.logic.first_fit_task import FirstFitTask
from re_rl.tasks.math.logic.plurality_task import PluralityTask
from re_rl.tasks.math.logic.floor_run_task import FloorRunTask
from re_rl.tasks.math.logic.saturate_count_task import SaturateCountTask
from re_rl.tasks.math.logic.undo_reg_task import UndoRegTask
from re_rl.tasks.math.logic.cover_point_task import CoverPointTask
from re_rl.tasks.math.logic.next_fit_task import NextFitTask
from re_rl.tasks.ml.neighbor_vote_task import NeighborVoteTask
from re_rl.tasks.ml.sgd_online_task import SgdOnlineTask
from re_rl.tasks.ml.grad_clip_task import GradClipTask
from re_rl.tasks.ml.weight_decay_task import WeightDecayTask
from re_rl.tasks.ml.early_stop_task import EarlyStopTask
from re_rl.tasks.ml.prototype_mean_task import PrototypeMeanTask
from re_rl.tasks.rl.trace_decay_task import TraceDecayTask
from re_rl.tasks.rl.actor_critic_task import ActorCriticTask
from re_rl.tasks.rl.ucb_bandit_task import UcbBanditTask
from re_rl.tasks.rl.target_sync_task import TargetSyncTask
from re_rl.tasks.rl.replay_fifo_task import ReplayFifoTask
from re_rl.tasks.rl.shape_reward_task import ShapeRewardTask
from re_rl.tasks.rl.eps_schedule_task import EpsScheduleTask
from re_rl.tasks.math.logic.scope_lookup_task import ScopeLookupTask
from re_rl.tasks.math.logic.lock_log_task import LockLogTask
from re_rl.tasks.math.logic.path_toll_task import PathTollTask
from re_rl.tasks.math.logic.backoff_wait_task import BackoffWaitTask
from re_rl.tasks.math.logic.priority_run_task import PriorityRunTask
from re_rl.tasks.math.logic.inbox_take_task import InboxTakeTask
from re_rl.tasks.math.logic.goal_match_task import GoalMatchTask
from re_rl.tasks.math.logic.craft_need_task import CraftNeedTask
from re_rl.tasks.math.logic.checkpoint_roll_task import CheckpointRollTask
from re_rl.tasks.math.logic.schema_check_task import SchemaCheckTask
from re_rl.tasks.math.algebra.infix_value_task import InfixValueTask
from re_rl.tasks.math.discrete.ballot_walk_task import BallotWalkTask
from re_rl.tasks.math.discrete.digit_root_task import DigitRootTask
from re_rl.tasks.math.discrete.crt_lift_task import CrtLiftTask
from re_rl.tasks.math.discrete.mod_order_task import ModOrderTask
from re_rl.tasks.math.logic.first_repeat_task import FirstRepeatTask
from re_rl.tasks.math.logic.coupon_cover_task import CouponCoverTask
from re_rl.tasks.math.logic.coin_weigh_task import CoinWeighTask
from re_rl.tasks.math.logic.two_color_task import TwoColorTask
from re_rl.tasks.math.discrete.lattice_sum_task import LatticeSumTask
from re_rl.tasks.math.algebra.horner_mod_task import HornerModTask
from re_rl.tasks.math.algebra.rational_root_task import RationalRootTask
from re_rl.tasks.math.analysis.geom_sum_task import GeomSumTask
from re_rl.tasks.math.discrete.cyclo_eval_task import CycloEvalTask
from re_rl.tasks.math.discrete.chebyshev_row_task import ChebyshevRowTask
from re_rl.tasks.math.discrete.hermite_row_task import HermiteRowTask
from re_rl.tasks.math.discrete.series_conv_task import SeriesConvTask
from re_rl.tasks.math.probability.transport_cost_task import TransportCostTask
from re_rl.tasks.math.discrete.pochhammer_task import PochhammerTask
from re_rl.tasks.math.discrete.binom_build_task import BinomBuildTask
from re_rl.tasks.math.discrete.farey_next_task import FareyNextTask
from re_rl.tasks.math.discrete.mobius_sum_task import MobiusSumTask
from re_rl.tasks.math.discrete.involution_count_task import InvolutionCountTask
from re_rl.tasks.math.discrete.jacobi_row_task import JacobiRowTask
from re_rl.tasks.math.discrete.ruler_sum_task import RulerSumTask
from re_rl.tasks.math.discrete.thue_count_task import ThueCountTask
from re_rl.tasks.math.discrete.aliquot_walk_task import AliquotWalkTask
from re_rl.tasks.math.discrete.carmichael_row_task import CarmichaelRowTask
from re_rl.tasks.math.discrete.cayley_trees_task import CayleyTreesTask
from re_rl.tasks.math.discrete.factoradic_task import FactoradicTask
from re_rl.tasks.math.discrete.stirling_first_task import StirlingFirstTask
from re_rl.tasks.math.discrete.bell_row_task import BellRowTask
from re_rl.tasks.math.discrete.andre_row_task import AndreRowTask
from re_rl.tasks.math.discrete.bernoulli_den_task import BernoulliDenTask
from re_rl.tasks.math.discrete.chebyshev_u_task import ChebyshevUTask
from re_rl.tasks.math.discrete.sigma_row_task import SigmaRowTask
from re_rl.tasks.math.discrete.prime_omega_task import PrimeOmegaTask
from re_rl.tasks.math.discrete.motzkin_row_task import MotzkinRowTask
from re_rl.tasks.math.discrete.primorial_task import PrimorialTask
from re_rl.tasks.math.discrete.rgs_rank_task import RgsRankTask
from re_rl.tasks.math.discrete.bernoulli_numer_task import BernoulliNumerTask
from re_rl.tasks.math.discrete.genocchi_row_task import GenocchiRowTask
from re_rl.tasks.math.discrete.kronecker_row_task import KroneckerRowTask
from re_rl.tasks.math.discrete.hook_length_task import HookLengthTask
from re_rl.tasks.math.discrete.legendre_frac_task import LegendreFracTask
from re_rl.tasks.math.discrete.laguerre_frac_task import LaguerreFracTask
from re_rl.tasks.math.discrete.harmonic_frac_task import HarmonicFracTask
from re_rl.tasks.math.discrete.eulerian_row_task import EulerianRowTask
from re_rl.tasks.math.discrete.fubini_row_task import FubiniRowTask
from re_rl.tasks.math.discrete.delannoy_row_task import DelannoyRowTask
from re_rl.tasks.math.discrete.tau_row_task import TauRowTask
from re_rl.tasks.math.discrete.prime_nu_task import PrimeNuTask
from re_rl.tasks.math.discrete.sopfr_row_task import SopfrRowTask
from re_rl.tasks.math.discrete.pell_row_task import PellRowTask
from re_rl.tasks.math.discrete.tribonacci_row_task import TribonacciRowTask
from re_rl.tasks.math.discrete.narayana_row_task import NarayanaRowTask
from re_rl.tasks.math.discrete.schroder_row_task import SchroderRowTask
from re_rl.tasks.math.discrete.gaussian_bin_task import GaussianBinTask
from re_rl.tasks.math.discrete.kolakoski_task import KolakoskiTask
from re_rl.tasks.math.discrete.cantor_pair_task import CantorPairTask
from re_rl.tasks.math.logic.horn_fire_task import HornFireTask
from re_rl.tasks.math.logic.carry_row_task import CarryRowTask
from re_rl.tasks.math.logic.lamp_trio_task import LampTrioTask
from re_rl.tasks.math.logic.parity_sheet_task import ParitySheetTask
from re_rl.tasks.math.logic.mux_index_task import MuxIndexTask
from re_rl.tasks.math.logic.jury_veto_task import JuryVetoTask
from re_rl.tasks.math.logic.gate_fold_task import GateFoldTask
from re_rl.tasks.math.logic.exactly_one_task import ExactlyOneTask
from re_rl.tasks.math.logic.knave_next_task import KnaveNextTask
from re_rl.tasks.math.logic.priority_bit_task import PriorityBitTask
from re_rl.tasks.math.logic.interval_merge_task import IntervalMergeTask
from re_rl.tasks.math.logic.cycle_count_task import CycleCountTask
from re_rl.tasks.math.logic.stack_perm_task import StackPermTask
from re_rl.tasks.math.logic.inversion_row_task import InversionRowTask
from re_rl.tasks.math.logic.run_length_task import RunLengthTask
from re_rl.tasks.math.logic.median_merge_task import MedianMergeTask
from re_rl.tasks.math.geometry.diag_cross_task import DiagCrossTask
from re_rl.tasks.math.geometry.billiard_cross_task import BilliardCrossTask
from re_rl.tasks.math.discrete.popcount_sum_task import PopcountSumTask
from re_rl.tasks.math.discrete.rencontres_row_task import RencontresRowTask
from re_rl.tasks.math.discrete.ballot_tri_task import BallotTriTask
from re_rl.tasks.math.discrete.dedekind_psi_task import DedekindPsiTask
from re_rl.tasks.math.discrete.jordan_tot_task import JordanTotTask
from re_rl.tasks.math.discrete.sylvester_row_task import SylvesterRowTask
from re_rl.tasks.math.discrete.lucas_row_task import LucasRowTask
from re_rl.tasks.math.discrete.liouville_row_task import LiouvilleRowTask
from re_rl.tasks.math.discrete.necklace_count_task import NecklaceCountTask
from re_rl.tasks.math.discrete.hamming_smooth_task import HammingSmoothTask
from re_rl.tasks.math.discrete.menage_count_task import MenageCountTask
from re_rl.tasks.math.logic.bracket_final_task import BracketFinalTask
from re_rl.tasks.math.logic.unit_prop_task import UnitPropTask
from re_rl.tasks.math.logic.gf2_solve_task import Gf2SolveTask
from re_rl.tasks.math.logic.resolve_proof_task import ResolveProofTask
from re_rl.tasks.math.logic.bool_eq_task import BoolEqTask
from re_rl.tasks.math.logic.assign_check_task import AssignCheckTask
from re_rl.tasks.math.logic.pigeon_place_task import PigeonPlaceTask
from re_rl.tasks.math.logic.kripke_box_task import KripkeBoxTask
from re_rl.tasks.math.logic.all_are_task import AllAreTask
from re_rl.tasks.math.logic.literal_clash_task import LiteralClashTask
from re_rl.tasks.math.logic.until_line_task import UntilLineTask
from re_rl.tasks.math.logic.dung_ground_task import DungGroundTask
from re_rl.tasks.math.logic.causal_do_task import CausalDoTask
from re_rl.tasks.math.logic.lukas_fold_task import LukasFoldTask
from re_rl.tasks.math.logic.doctrinal_task import DoctrinalTask
from re_rl.tasks.math.logic.knows_line_task import KnowsLineTask
from re_rl.tasks.math.logic.rough_set_task import RoughSetTask
from re_rl.tasks.math.logic.naf_fire_task import NafFireTask
from re_rl.tasks.math.logic.agenda_vote_task import AgendaVoteTask
from re_rl.tasks.math.logic.short_circuit_task import ShortCircuitTask
from re_rl.tasks.math.logic.ref_count_task import RefCountTask
from re_rl.tasks.math.logic.wrap_index_task import WrapIndexTask
from re_rl.tasks.math.logic.bit_prog_task import BitProgTask
from re_rl.tasks.math.logic.break_sum_task import BreakSumTask
from re_rl.tasks.math.logic.bounds_step_task import BoundsStepTask
from re_rl.tasks.math.logic.reg_swap_task import RegSwapTask
from re_rl.tasks.math.logic.elif_pick_task import ElifPickTask
from re_rl.tasks.math.logic.post_inc_task import PostIncTask
from re_rl.tasks.math.logic.min_hold_task import MinHoldTask
from re_rl.tasks.math.logic.jump_add_task import JumpAddTask
from re_rl.tasks.math.logic.div_chain_task import DivChainTask
from re_rl.tasks.math.logic.clamp_add_task import ClampAddTask
from re_rl.tasks.math.logic.ptr_walk_task import PtrWalkTask
from re_rl.tasks.math.logic.continue_sum_task import ContinueSumTask
from re_rl.tasks.math.logic.delay_line_task import DelayLineTask
from re_rl.tasks.math.logic.switch_case_task import SwitchCaseTask
from re_rl.tasks.math.logic.digit_scan_task import DigitScanTask
from re_rl.tasks.math.logic.rot_nibble_task import RotNibbleTask
from re_rl.tasks.math.logic.buf_len_task import BufLenTask
from re_rl.tasks.math.logic.cmp_branch_task import CmpBranchTask
from re_rl.tasks.math.logic.bit_set_task import BitSetTask
from re_rl.tasks.math.logic.cell_write_task import CellWriteTask
from re_rl.tasks.math.logic.lcg_step_task import LcgStepTask
from re_rl.tasks.math.logic.two_stack_task import TwoStackTask
from re_rl.tasks.math.logic.sorted_insert_task import SortedInsertTask
from re_rl.tasks.math.logic.brace_pair_task import BracePairTask
from re_rl.tasks.math.logic.hash_probe_task import HashProbeTask
from re_rl.tasks.math.logic.part_count_task import PartCountTask
from re_rl.tasks.math.logic.fill_forward_task import FillForwardTask
from re_rl.tasks.math.logic.xor_fold_task import XorFoldTask
from re_rl.tasks.math.logic.bubble_pass_task import BubblePassTask
from re_rl.tasks.math.logic.mtf_list_task import MtfListTask
from re_rl.tasks.math.logic.turnstile_task import TurnstileTask
from re_rl.tasks.math.logic.hamming_step_task import HammingStepTask
from re_rl.tasks.math.logic.row_major_task import RowMajorTask
from re_rl.tasks.math.logic.union_count_task import UnionCountTask
from re_rl.tasks.math.logic.trie_node_task import TrieNodeTask
from re_rl.tasks.math.logic.minute_add_task import MinuteAddTask
from re_rl.tasks.math.logic.mod_accum_task import ModAccumTask
from re_rl.tasks.math.logic.nfa_run_task import NfaRunTask
from re_rl.tasks.math.logic.moore_run_task import MooreRunTask
from re_rl.tasks.math.logic.sync_run_task import SyncRunTask
from re_rl.tasks.math.logic.meet_run_task import MeetRunTask
from re_rl.tasks.math.logic.lfsr_run_task import LfsrRunTask
from re_rl.tasks.math.logic.crc_rem_task import CrcRemTask
from re_rl.tasks.math.logic.feistel_run_task import FeistelRunTask
from re_rl.tasks.math.logic.elgamal_enc_task import ElgamalEncTask
from re_rl.tasks.math.logic.fact_base_task import FactBaseTask
from re_rl.tasks.math.logic.cas_cell_task import CasCellTask
from re_rl.tasks.math.logic.memo_call_task import MemoCallTask
from re_rl.tasks.math.logic.skip_fit_task import SkipFitTask
from re_rl.tasks.math.logic.handoff_ask_task import HandoffAskTask
from re_rl.tasks.math.logic.reject_add_task import RejectAddTask
from re_rl.tasks.math.logic.ref_resolve_task import RefResolveTask
from re_rl.tasks.math.logic.belief_vote_task import BeliefVoteTask
from re_rl.tasks.math.logic.join_wait_task import JoinWaitTask
from re_rl.tasks.math.logic.audit_sum_task import AuditSumTask
from re_rl.tasks.math.probability.draw_out_task import DrawOutTask
from re_rl.tasks.math.probability.die_build_task import DieBuildTask
from re_rl.tasks.math.probability.rank_stop_task import RankStopTask
from re_rl.tasks.math.probability.day_clash_task import DayClashTask
from re_rl.tasks.math.probability.group_mean_task import GroupMeanTask
from re_rl.tasks.math.probability.safe_bits_task import SafeBitsTask
from re_rl.tasks.math.probability.first_to_task import FirstToTask
from re_rl.tasks.math.probability.odds_mass_task import OddsMassTask
from re_rl.tasks.math.probability.simpson_pool_task import SimpsonPoolTask
from re_rl.tasks.math.logic.job_slack_task import JobSlackTask
from re_rl.tasks.math.logic.pair_vote_task import PairVoteTask
from re_rl.tasks.math.probability.screen_count_task import ScreenCountTask
from re_rl.tasks.math.applied.burn_balance_task import BurnBalanceTask
from re_rl.tasks.math.discrete.h_index_task import HIndexTask
from re_rl.tasks.math.logic.allele_fit_task import AlleleFitTask
from re_rl.tasks.math.logic.pareto_keep_task import ParetoKeepTask
from re_rl.tasks.math.abstract_algebra.perm_order_task import PermOrderTask
from re_rl.tasks.math.abstract_algebra.perm_conj_task import PermConjTask
from re_rl.tasks.math.abstract_algebra.add_orbit_task import AddOrbitTask
from re_rl.tasks.math.abstract_algebra.unit_mod_task import UnitModTask
from re_rl.tasks.math.abstract_algebra.nil_index_task import NilIndexTask
from re_rl.tasks.math.abstract_algebra.mod_poly_task import ModPolyTask
from re_rl.tasks.math.abstract_algebra.heisen_mul_task import HeisenMulTask
from re_rl.tasks.math.abstract_algebra.coset_rep_task import CosetRepTask
from re_rl.tasks.math.abstract_algebra.betti_mod_task import BettiModTask
from re_rl.tasks.math.abstract_algebra.curve_add_task import CurveAddTask
from re_rl.tasks.math.abstract_algebra.smith_inv_task import SmithInvTask
from re_rl.tasks.math.discrete.form_reduce_task import FormReduceTask
from re_rl.tasks.math.algebra.res_chain_task import ResChainTask
from re_rl.tasks.math.algebra.sturm_root_task import SturmRootTask
from re_rl.tasks.math.logic.anf_fold_task import AnfFoldTask
from re_rl.tasks.math.probability.coin_wait_task import CoinWaitTask
from re_rl.tasks.math.probability.ruin_time_task import RuinTimeTask
from re_rl.tasks.math.probability.mix_count_task import MixCountTask
from re_rl.tasks.math.probability.repeat_test_task import RepeatTestTask
from re_rl.tasks.math.probability.group_var_task import GroupVarTask
from re_rl.tasks.math.probability.pivot_cost_task import PivotCostTask
from re_rl.tasks.ml.hard_attend_task import HardAttendTask
from re_rl.tasks.ml.max_pool_task import MaxPoolTask
from re_rl.tasks.ml.adam_tick_task import AdamTickTask
from re_rl.tasks.ml.rnn_add_task import RnnAddTask
from re_rl.tasks.ml.margin_push_task import MarginPushTask
from re_rl.tasks.ml.template_lag_task import TemplateLagTask
from re_rl.tasks.ml.roc_walk_task import RocWalkTask
from re_rl.tasks.ml.ema_loss_task import EmaLossTask
from re_rl.tasks.ml.lr_decay_task import LrDecayTask
from re_rl.tasks.ml.batch_grad_task import BatchGradTask
from re_rl.tasks.ml.best_margin_task import BestMarginTask
from re_rl.tasks.ml.ctc_collapse_task import CtcCollapseTask
from re_rl.tasks.ml.relu_chain_task import ReluChainTask
from re_rl.tasks.ml.causal_pick_task import CausalPickTask
from re_rl.tasks.ml.triplet_gap_task import TripletGapTask
from re_rl.tasks.ml.beam_keep_task import BeamKeepTask
from re_rl.tasks.ml.draft_accept_task import DraftAcceptTask
from re_rl.tasks.ml.class_margin_task import ClassMarginTask
from re_rl.tasks.ml.bin_tally_task import BinTallyTask
from re_rl.tasks.ml.grad_accum_task import GradAccumTask
from re_rl.tasks.ml.skip_add_task import SkipAddTask
from re_rl.tasks.rl.online_base_task import OnlineBaseTask
from re_rl.tasks.rl.td_clip_task import TdClipTask
from re_rl.tasks.rl.count_bonus_task import CountBonusTask
from re_rl.tasks.rl.option_hold_task import OptionHoldTask
from re_rl.tasks.rl.policy_eval_task import PolicyEvalTask
from re_rl.tasks.rl.hindsight_hit_task import HindsightHitTask
from re_rl.tasks.rl.legal_greedy_task import LegalGreedyTask
from re_rl.tasks.rl.reward_machine_task import RewardMachineTask
from re_rl.tasks.rl.episode_cut_task import EpisodeCutTask
from re_rl.tasks.rl.best_reply_task import BestReplyTask
from re_rl.tasks.rl.arm_rate_task import ArmRateTask
from re_rl.tasks.rl.budget_step_task import BudgetStepTask
from re_rl.tasks.rl.done_boot_task import DoneBootTask
from re_rl.tasks.rl.greedy_gap_task import GreedyGapTask
from re_rl.tasks.rl.switch_cost_task import SwitchCostTask
from re_rl.tasks.math.geometry.shadow_height_task import ShadowHeightTask
from re_rl.tasks.math.geometry.manhattan_paths_task import ManhattanPathsTask
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
        texts.t('s0', language),
        texts.t('s1', language),
        texts.t('s2', language),
        
        # Геометрические аналогии
        texts.t('s3', language),
        texts.t('s4', language),
        
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
generate_random_work_rates_task = _mk_generator(WorkRatesTask)
generate_random_mixture_concentration_task = _mk_generator(MixtureConcentrationTask)
generate_random_ratio_split_task = _mk_generator(RatioSplitTask)
generate_random_clock_hands_task = _mk_generator(ClockHandsTask)
generate_random_polygon_angles_task = _mk_generator(PolygonAnglesTask)
generate_random_grid_diagonal_task = _mk_generator(GridDiagonalTask)
generate_random_triangle_sides_task = _mk_generator(TriangleSidesTask)
generate_random_divisor_sum_task = _mk_generator(DivisorSumTask)
generate_random_digital_root_task = _mk_generator(DigitalRootTask)
generate_random_dice_ways_task = _mk_generator(DiceWaysTask)
generate_random_map_scale_task = _mk_generator(MapScaleTask)
generate_random_age_gap_task = _mk_generator(AgeGapTask)
generate_random_crew_work_task = _mk_generator(CrewWorkTask)
generate_random_mix_chain_task = _mk_generator(MixChainTask)
generate_random_mod_chain_task = _mk_generator(ModChainTask)
generate_random_gcd_chain_task = _mk_generator(GcdChainTask)
generate_random_recurrence_walk_task = _mk_generator(RecurrenceWalkTask)
generate_random_turtle_walk_task = _mk_generator(TurtleWalkTask)
generate_random_portal_walk_task = _mk_generator(PortalWalkTask)
generate_random_horner_eval_task = _mk_generator(HornerEvalTask)
generate_random_ledger_guard_task = _mk_generator(LedgerGuardTask)
generate_random_truck_trips_task = _mk_generator(TruckTripsTask)
generate_random_door_toggles_task = _mk_generator(DoorTogglesTask)
generate_random_greedy_coins_task = _mk_generator(GreedyCoinsTask)
generate_random_walk_range_task = _mk_generator(WalkRangeTask)
generate_random_carry_add_task = _mk_generator(CarryAddTask)
generate_random_line_infection_task = _mk_generator(LineInfectionTask)
generate_random_corridor_keys_task = _mk_generator(CorridorKeysTask)
generate_random_next_greater_task = _mk_generator(NextGreaterTask)
generate_random_window_max_task = _mk_generator(WindowMaxTask)
generate_random_two_pointer_merge_task = _mk_generator(TwoPointerMergeTask)
generate_random_cooldown_schedule_task = _mk_generator(CooldownScheduleTask)
generate_random_pancake_trace_task = _mk_generator(PancakeTraceTask)
generate_random_bracket_scan_task = _mk_generator(BracketScanTask)
generate_random_kmeans_rounds_task = _mk_generator(KMeansRoundsTask)
generate_random_bayes_updates_task = _mk_generator(BayesUpdatesTask)
generate_random_polya_urn_task = _mk_generator(PolyaUrnTask)
generate_random_policy_rollout_task = _mk_generator(PolicyRolloutTask)
generate_random_boost_weights_task = _mk_generator(BoostWeightsTask)
generate_random_momentum_sgd_task = _mk_generator(MomentumSgdTask)
generate_random_decision_list_task = _mk_generator(DecisionListTask)
generate_random_td_table_task = _mk_generator(TdTableTask)
generate_random_extended_euclid_task = _mk_generator(ExtendedEuclidTask)
generate_random_crt_chain_task = _mk_generator(CrtChainTask)
generate_random_cf_expand_task = _mk_generator(CfExpandTask)
generate_random_nim_sum_task = _mk_generator(NimSumTask)
generate_random_difference_table_task = _mk_generator(DifferenceTableTask)
generate_random_sandpile_path_task = _mk_generator(SandpilePathTask)
generate_random_markov_steps_task = _mk_generator(MarkovStepsTask)
generate_random_sir_ticks_task = _mk_generator(SirTicksTask)
generate_random_poly_div_task = _mk_generator(PolyDivTask)
generate_random_johnson_span_task = _mk_generator(JohnsonSpanTask)
generate_random_lights_path_task = _mk_generator(LightsPathTask)
generate_random_domino_chain_task = _mk_generator(DominoChainTask)
generate_random_bound_scan_task = _mk_generator(BoundScanTask)
generate_random_claim_count_task = _mk_generator(ClaimCountTask)
generate_random_quorum_rise_task = _mk_generator(QuorumRiseTask)
generate_random_hat_line_task = _mk_generator(HatLineTask)
generate_random_reagent_chain_task = _mk_generator(ReagentChainTask)
generate_random_tax_brackets_task = _mk_generator(TaxBracketsTask)
generate_random_codon_scan_task = _mk_generator(CodonScanTask)
generate_random_dose_schedule_task = _mk_generator(DoseScheduleTask)
generate_random_melody_walk_task = _mk_generator(MelodyWalkTask)
generate_random_fifo_cost_task = _mk_generator(FifoCostTask)
generate_random_borda_count_task = _mk_generator(BordaCountTask)
generate_random_shift_add_task = _mk_generator(ShiftAddTask)
generate_random_rally_lead_task = _mk_generator(RallyLeadTask)
generate_random_pascal_row_task = _mk_generator(PascalRowTask)
generate_random_fraction_ops_task = _mk_generator(FractionOpsTask)
generate_random_stern_path_task = _mk_generator(SternPathTask)
generate_random_partition_count_task = _mk_generator(PartitionCountTask)
generate_random_derange_count_task = _mk_generator(DerangeCountTask)
generate_random_gauss_mul_task = _mk_generator(GaussMulTask)
generate_random_perm_compose_task = _mk_generator(PermComposeTask)
generate_random_cover_span_task = _mk_generator(CoverSpanTask)
generate_random_reverse_add_task = _mk_generator(ReverseAddTask)
generate_random_stream_median_task = _mk_generator(StreamMedianTask)
generate_random_totient_row_task = _mk_generator(TotientRowTask)
generate_random_coprime_count_task = _mk_generator(CoprimeCountTask)
generate_random_digit_div_task = _mk_generator(DigitDivTask)
generate_random_tree_depth_task = _mk_generator(TreeDepthTask)
generate_random_sign_walk_task = _mk_generator(SignWalkTask)
generate_random_perm_rank_task = _mk_generator(PermRankTask)
generate_random_lcm_rise_task = _mk_generator(LcmRiseTask)
generate_random_zigzag_row_task = _mk_generator(ZigzagRowTask)
generate_random_record_highs_task = _mk_generator(RecordHighsTask)
generate_random_sum_kinds_task = _mk_generator(SumKindsTask)
generate_random_fib_word_task = _mk_generator(FibWordTask)
generate_random_mode_track_task = _mk_generator(ModeTrackTask)
generate_random_look_say_task = _mk_generator(LookSayTask)
generate_random_zeckendorf_task = _mk_generator(ZeckendorfTask)
generate_random_roman_value_task = _mk_generator(RomanValueTask)
generate_random_digit_stream_task = _mk_generator(DigitStreamTask)
generate_random_deque_trace_task = _mk_generator(DequeTraceTask)
generate_random_dragon_fold_task = _mk_generator(DragonFoldTask)
generate_random_permanent_task = _mk_generator(PermanentTask)
generate_random_bead_count_task = _mk_generator(BeadCountTask)
generate_random_negabase_task = _mk_generator(NegabaseTask)
generate_random_ulam_walk_task = _mk_generator(UlamWalkTask)
generate_random_luhn_sum_task = _mk_generator(LuhnSumTask)
generate_random_kaprekar_step_task = _mk_generator(KaprekarStepTask)
generate_random_morton_code_task = _mk_generator(MortonCodeTask)
generate_random_stock_span_task = _mk_generator(StockSpanTask)
generate_random_candy_row_task = _mk_generator(CandyRowTask)
generate_random_digit_fact_task = _mk_generator(DigitFactTask)
generate_random_recaman_task = _mk_generator(RecamanTask)
generate_random_xor_basis_task = _mk_generator(XorBasisTask)
generate_random_palindrome_radius_task = _mk_generator(PalindromeRadiusTask)
generate_random_squarefree_row_task = _mk_generator(SquarefreeRowTask)
generate_random_fenwick_sum_task = _mk_generator(FenwickSumTask)
generate_random_sparse_min_task = _mk_generator(SparseMinTask)
generate_random_z_array_task = _mk_generator(ZArrayTask)
generate_random_selection_swaps_task = _mk_generator(SelectionSwapsTask)
generate_random_rho_cycle_task = _mk_generator(RhoCycleTask)
generate_random_tree_times_task = _mk_generator(TreeTimesTask)
generate_random_dutch_flag_task = _mk_generator(DutchFlagTask)
generate_random_window_distinct_task = _mk_generator(WindowDistinctTask)
generate_random_stable_place_task = _mk_generator(StablePlaceTask)
generate_random_naive_find_task = _mk_generator(NaiveFindTask)
generate_random_budget_take_task = _mk_generator(BudgetTakeTask)
generate_random_skip_op_task = _mk_generator(SkipOpTask)
generate_random_retry_goal_task = _mk_generator(RetryGoalTask)
generate_random_signal_edges_task = _mk_generator(SignalEdgesTask)
generate_random_plan_gate_task = _mk_generator(PlanGateTask)
generate_random_tool_pick_task = _mk_generator(ToolPickTask)
generate_random_diff_count_task = _mk_generator(DiffCountTask)
generate_random_cell_patch_task = _mk_generator(CellPatchTask)
generate_random_pred_scan_task = _mk_generator(PredScanTask)
generate_random_rate_limit_task = _mk_generator(RateLimitTask)
generate_random_lateness_task = _mk_generator(LatenessTask)
generate_random_switch_flip_task = _mk_generator(SwitchFlipTask)
generate_random_turn_signs_task = _mk_generator(TurnSignsTask)
generate_random_first_fit_task = _mk_generator(FirstFitTask)
generate_random_plurality_task = _mk_generator(PluralityTask)
generate_random_floor_run_task = _mk_generator(FloorRunTask)
generate_random_saturate_count_task = _mk_generator(SaturateCountTask)
generate_random_undo_reg_task = _mk_generator(UndoRegTask)
generate_random_cover_point_task = _mk_generator(CoverPointTask)
generate_random_next_fit_task = _mk_generator(NextFitTask)
generate_random_neighbor_vote_task = _mk_generator(NeighborVoteTask)
generate_random_sgd_online_task = _mk_generator(SgdOnlineTask)
generate_random_grad_clip_task = _mk_generator(GradClipTask)
generate_random_weight_decay_task = _mk_generator(WeightDecayTask)
generate_random_early_stop_task = _mk_generator(EarlyStopTask)
generate_random_prototype_mean_task = _mk_generator(PrototypeMeanTask)
generate_random_trace_decay_task = _mk_generator(TraceDecayTask)
generate_random_actor_critic_task = _mk_generator(ActorCriticTask)
generate_random_ucb_bandit_task = _mk_generator(UcbBanditTask)
generate_random_target_sync_task = _mk_generator(TargetSyncTask)
generate_random_replay_fifo_task = _mk_generator(ReplayFifoTask)
generate_random_shape_reward_task = _mk_generator(ShapeRewardTask)
generate_random_eps_schedule_task = _mk_generator(EpsScheduleTask)
generate_random_scope_lookup_task = _mk_generator(ScopeLookupTask)
generate_random_lock_log_task = _mk_generator(LockLogTask)
generate_random_path_toll_task = _mk_generator(PathTollTask)
generate_random_backoff_wait_task = _mk_generator(BackoffWaitTask)
generate_random_priority_run_task = _mk_generator(PriorityRunTask)
generate_random_inbox_take_task = _mk_generator(InboxTakeTask)
generate_random_goal_match_task = _mk_generator(GoalMatchTask)
generate_random_craft_need_task = _mk_generator(CraftNeedTask)
generate_random_checkpoint_roll_task = _mk_generator(CheckpointRollTask)
generate_random_schema_check_task = _mk_generator(SchemaCheckTask)
generate_random_infix_value_task = _mk_generator(InfixValueTask)
generate_random_ballot_walk_task = _mk_generator(BallotWalkTask)
generate_random_digit_root_task = _mk_generator(DigitRootTask)
generate_random_crt_lift_task = _mk_generator(CrtLiftTask)
generate_random_mod_order_task = _mk_generator(ModOrderTask)
generate_random_first_repeat_task = _mk_generator(FirstRepeatTask)
generate_random_coupon_cover_task = _mk_generator(CouponCoverTask)
generate_random_coin_weigh_task = _mk_generator(CoinWeighTask)
generate_random_two_color_task = _mk_generator(TwoColorTask)
generate_random_lattice_sum_task = _mk_generator(LatticeSumTask)
generate_random_horner_mod_task = _mk_generator(HornerModTask)
generate_random_rational_root_task = _mk_generator(RationalRootTask)
generate_random_geom_sum_task = _mk_generator(GeomSumTask)
generate_random_cyclo_eval_task = _mk_generator(CycloEvalTask)
generate_random_chebyshev_row_task = _mk_generator(ChebyshevRowTask)
generate_random_hermite_row_task = _mk_generator(HermiteRowTask)
generate_random_series_conv_task = _mk_generator(SeriesConvTask)
generate_random_transport_cost_task = _mk_generator(TransportCostTask)
generate_random_pochhammer_task = _mk_generator(PochhammerTask)
generate_random_binom_build_task = _mk_generator(BinomBuildTask)
generate_random_farey_next_task = _mk_generator(FareyNextTask)
generate_random_mobius_sum_task = _mk_generator(MobiusSumTask)
generate_random_involution_count_task = _mk_generator(InvolutionCountTask)
generate_random_jacobi_row_task = _mk_generator(JacobiRowTask)
generate_random_ruler_sum_task = _mk_generator(RulerSumTask)
generate_random_thue_count_task = _mk_generator(ThueCountTask)
generate_random_aliquot_walk_task = _mk_generator(AliquotWalkTask)
generate_random_carmichael_row_task = _mk_generator(CarmichaelRowTask)
generate_random_cayley_trees_task = _mk_generator(CayleyTreesTask)
generate_random_factoradic_task = _mk_generator(FactoradicTask)
generate_random_stirling_first_task = _mk_generator(StirlingFirstTask)
generate_random_bell_row_task = _mk_generator(BellRowTask)
generate_random_andre_row_task = _mk_generator(AndreRowTask)
generate_random_bernoulli_den_task = _mk_generator(BernoulliDenTask)
generate_random_chebyshev_u_task = _mk_generator(ChebyshevUTask)
generate_random_sigma_row_task = _mk_generator(SigmaRowTask)
generate_random_prime_omega_task = _mk_generator(PrimeOmegaTask)
generate_random_motzkin_row_task = _mk_generator(MotzkinRowTask)
generate_random_primorial_task = _mk_generator(PrimorialTask)
generate_random_rgs_rank_task = _mk_generator(RgsRankTask)
generate_random_bernoulli_numer_task = _mk_generator(BernoulliNumerTask)
generate_random_genocchi_row_task = _mk_generator(GenocchiRowTask)
generate_random_kronecker_row_task = _mk_generator(KroneckerRowTask)
generate_random_hook_length_task = _mk_generator(HookLengthTask)
generate_random_legendre_frac_task = _mk_generator(LegendreFracTask)
generate_random_laguerre_frac_task = _mk_generator(LaguerreFracTask)
generate_random_harmonic_frac_task = _mk_generator(HarmonicFracTask)
generate_random_eulerian_row_task = _mk_generator(EulerianRowTask)
generate_random_fubini_row_task = _mk_generator(FubiniRowTask)
generate_random_delannoy_row_task = _mk_generator(DelannoyRowTask)
generate_random_tau_row_task = _mk_generator(TauRowTask)
generate_random_prime_nu_task = _mk_generator(PrimeNuTask)
generate_random_sopfr_row_task = _mk_generator(SopfrRowTask)
generate_random_pell_row_task = _mk_generator(PellRowTask)
generate_random_tribonacci_row_task = _mk_generator(TribonacciRowTask)
generate_random_narayana_row_task = _mk_generator(NarayanaRowTask)
generate_random_schroder_row_task = _mk_generator(SchroderRowTask)
generate_random_gaussian_bin_task = _mk_generator(GaussianBinTask)
generate_random_kolakoski_task = _mk_generator(KolakoskiTask)
generate_random_cantor_pair_task = _mk_generator(CantorPairTask)
generate_random_horn_fire_task = _mk_generator(HornFireTask)
generate_random_carry_row_task = _mk_generator(CarryRowTask)
generate_random_lamp_trio_task = _mk_generator(LampTrioTask)
generate_random_parity_sheet_task = _mk_generator(ParitySheetTask)
generate_random_mux_index_task = _mk_generator(MuxIndexTask)
generate_random_jury_veto_task = _mk_generator(JuryVetoTask)
generate_random_gate_fold_task = _mk_generator(GateFoldTask)
generate_random_exactly_one_task = _mk_generator(ExactlyOneTask)
generate_random_knave_next_task = _mk_generator(KnaveNextTask)
generate_random_priority_bit_task = _mk_generator(PriorityBitTask)
generate_random_interval_merge_task = _mk_generator(IntervalMergeTask)
generate_random_cycle_count_task = _mk_generator(CycleCountTask)
generate_random_stack_perm_task = _mk_generator(StackPermTask)
generate_random_inversion_row_task = _mk_generator(InversionRowTask)
generate_random_run_length_task = _mk_generator(RunLengthTask)
generate_random_median_merge_task = _mk_generator(MedianMergeTask)
generate_random_diag_cross_task = _mk_generator(DiagCrossTask)
generate_random_billiard_cross_task = _mk_generator(BilliardCrossTask)
generate_random_popcount_sum_task = _mk_generator(PopcountSumTask)
generate_random_rencontres_row_task = _mk_generator(RencontresRowTask)
generate_random_ballot_tri_task = _mk_generator(BallotTriTask)
generate_random_dedekind_psi_task = _mk_generator(DedekindPsiTask)
generate_random_jordan_tot_task = _mk_generator(JordanTotTask)
generate_random_sylvester_row_task = _mk_generator(SylvesterRowTask)
generate_random_lucas_row_task = _mk_generator(LucasRowTask)
generate_random_liouville_row_task = _mk_generator(LiouvilleRowTask)
generate_random_necklace_count_task = _mk_generator(NecklaceCountTask)
generate_random_hamming_smooth_task = _mk_generator(HammingSmoothTask)
generate_random_menage_count_task = _mk_generator(MenageCountTask)
generate_random_bracket_final_task = _mk_generator(BracketFinalTask)
generate_random_unit_prop_task = _mk_generator(UnitPropTask)
generate_random_gf2_solve_task = _mk_generator(Gf2SolveTask)
generate_random_resolve_proof_task = _mk_generator(ResolveProofTask)
generate_random_bool_eq_task = _mk_generator(BoolEqTask)
generate_random_assign_check_task = _mk_generator(AssignCheckTask)
generate_random_pigeon_place_task = _mk_generator(PigeonPlaceTask)
generate_random_kripke_box_task = _mk_generator(KripkeBoxTask)
generate_random_all_are_task = _mk_generator(AllAreTask)
generate_random_literal_clash_task = _mk_generator(LiteralClashTask)
generate_random_until_line_task = _mk_generator(UntilLineTask)
generate_random_dung_ground_task = _mk_generator(DungGroundTask)
generate_random_causal_do_task = _mk_generator(CausalDoTask)
generate_random_lukas_fold_task = _mk_generator(LukasFoldTask)
generate_random_doctrinal_task = _mk_generator(DoctrinalTask)
generate_random_knows_line_task = _mk_generator(KnowsLineTask)
generate_random_rough_set_task = _mk_generator(RoughSetTask)
generate_random_naf_fire_task = _mk_generator(NafFireTask)
generate_random_agenda_vote_task = _mk_generator(AgendaVoteTask)
generate_random_short_circuit_task = _mk_generator(ShortCircuitTask)
generate_random_ref_count_task = _mk_generator(RefCountTask)
generate_random_wrap_index_task = _mk_generator(WrapIndexTask)
generate_random_bit_prog_task = _mk_generator(BitProgTask)
generate_random_break_sum_task = _mk_generator(BreakSumTask)
generate_random_bounds_step_task = _mk_generator(BoundsStepTask)
generate_random_reg_swap_task = _mk_generator(RegSwapTask)
generate_random_elif_pick_task = _mk_generator(ElifPickTask)
generate_random_post_inc_task = _mk_generator(PostIncTask)
generate_random_min_hold_task = _mk_generator(MinHoldTask)
generate_random_jump_add_task = _mk_generator(JumpAddTask)
generate_random_div_chain_task = _mk_generator(DivChainTask)
generate_random_clamp_add_task = _mk_generator(ClampAddTask)
generate_random_ptr_walk_task = _mk_generator(PtrWalkTask)
generate_random_continue_sum_task = _mk_generator(ContinueSumTask)
generate_random_delay_line_task = _mk_generator(DelayLineTask)
generate_random_switch_case_task = _mk_generator(SwitchCaseTask)
generate_random_digit_scan_task = _mk_generator(DigitScanTask)
generate_random_rot_nibble_task = _mk_generator(RotNibbleTask)
generate_random_buf_len_task = _mk_generator(BufLenTask)
generate_random_cmp_branch_task = _mk_generator(CmpBranchTask)
generate_random_bit_set_task = _mk_generator(BitSetTask)
generate_random_cell_write_task = _mk_generator(CellWriteTask)
generate_random_lcg_step_task = _mk_generator(LcgStepTask)
generate_random_two_stack_task = _mk_generator(TwoStackTask)
generate_random_sorted_insert_task = _mk_generator(SortedInsertTask)
generate_random_brace_pair_task = _mk_generator(BracePairTask)
generate_random_hash_probe_task = _mk_generator(HashProbeTask)
generate_random_part_count_task = _mk_generator(PartCountTask)
generate_random_fill_forward_task = _mk_generator(FillForwardTask)
generate_random_xor_fold_task = _mk_generator(XorFoldTask)
generate_random_bubble_pass_task = _mk_generator(BubblePassTask)
generate_random_mtf_list_task = _mk_generator(MtfListTask)
generate_random_turnstile_task = _mk_generator(TurnstileTask)
generate_random_hamming_step_task = _mk_generator(HammingStepTask)
generate_random_row_major_task = _mk_generator(RowMajorTask)
generate_random_union_count_task = _mk_generator(UnionCountTask)
generate_random_trie_node_task = _mk_generator(TrieNodeTask)
generate_random_minute_add_task = _mk_generator(MinuteAddTask)
generate_random_mod_accum_task = _mk_generator(ModAccumTask)
generate_random_nfa_run_task = _mk_generator(NfaRunTask)
generate_random_moore_run_task = _mk_generator(MooreRunTask)
generate_random_sync_run_task = _mk_generator(SyncRunTask)
generate_random_meet_run_task = _mk_generator(MeetRunTask)
generate_random_lfsr_run_task = _mk_generator(LfsrRunTask)
generate_random_crc_rem_task = _mk_generator(CrcRemTask)
generate_random_feistel_run_task = _mk_generator(FeistelRunTask)
generate_random_elgamal_enc_task = _mk_generator(ElgamalEncTask)
generate_random_fact_base_task = _mk_generator(FactBaseTask)
generate_random_cas_cell_task = _mk_generator(CasCellTask)
generate_random_memo_call_task = _mk_generator(MemoCallTask)
generate_random_skip_fit_task = _mk_generator(SkipFitTask)
generate_random_handoff_ask_task = _mk_generator(HandoffAskTask)
generate_random_reject_add_task = _mk_generator(RejectAddTask)
generate_random_ref_resolve_task = _mk_generator(RefResolveTask)
generate_random_belief_vote_task = _mk_generator(BeliefVoteTask)
generate_random_join_wait_task = _mk_generator(JoinWaitTask)
generate_random_audit_sum_task = _mk_generator(AuditSumTask)
generate_random_draw_out_task = _mk_generator(DrawOutTask)
generate_random_die_build_task = _mk_generator(DieBuildTask)
generate_random_rank_stop_task = _mk_generator(RankStopTask)
generate_random_day_clash_task = _mk_generator(DayClashTask)
generate_random_group_mean_task = _mk_generator(GroupMeanTask)
generate_random_safe_bits_task = _mk_generator(SafeBitsTask)
generate_random_first_to_task = _mk_generator(FirstToTask)
generate_random_odds_mass_task = _mk_generator(OddsMassTask)
generate_random_simpson_pool_task = _mk_generator(SimpsonPoolTask)
generate_random_job_slack_task = _mk_generator(JobSlackTask)
generate_random_pair_vote_task = _mk_generator(PairVoteTask)
generate_random_screen_count_task = _mk_generator(ScreenCountTask)
generate_random_burn_balance_task = _mk_generator(BurnBalanceTask)
generate_random_h_index_task = _mk_generator(HIndexTask)
generate_random_allele_fit_task = _mk_generator(AlleleFitTask)
generate_random_pareto_keep_task = _mk_generator(ParetoKeepTask)
generate_random_perm_order_task = _mk_generator(PermOrderTask)
generate_random_perm_conj_task = _mk_generator(PermConjTask)
generate_random_add_orbit_task = _mk_generator(AddOrbitTask)
generate_random_unit_mod_task = _mk_generator(UnitModTask)
generate_random_nil_index_task = _mk_generator(NilIndexTask)
generate_random_mod_poly_task = _mk_generator(ModPolyTask)
generate_random_heisen_mul_task = _mk_generator(HeisenMulTask)
generate_random_coset_rep_task = _mk_generator(CosetRepTask)
generate_random_betti_mod_task = _mk_generator(BettiModTask)
generate_random_curve_add_task = _mk_generator(CurveAddTask)
generate_random_smith_inv_task = _mk_generator(SmithInvTask)
generate_random_form_reduce_task = _mk_generator(FormReduceTask)
generate_random_res_chain_task = _mk_generator(ResChainTask)
generate_random_sturm_root_task = _mk_generator(SturmRootTask)
generate_random_anf_fold_task = _mk_generator(AnfFoldTask)
generate_random_coin_wait_task = _mk_generator(CoinWaitTask)
generate_random_ruin_time_task = _mk_generator(RuinTimeTask)
generate_random_mix_count_task = _mk_generator(MixCountTask)
generate_random_repeat_test_task = _mk_generator(RepeatTestTask)
generate_random_group_var_task = _mk_generator(GroupVarTask)
generate_random_pivot_cost_task = _mk_generator(PivotCostTask)
generate_random_hard_attend_task = _mk_generator(HardAttendTask)
generate_random_max_pool_task = _mk_generator(MaxPoolTask)
generate_random_adam_tick_task = _mk_generator(AdamTickTask)
generate_random_rnn_add_task = _mk_generator(RnnAddTask)
generate_random_margin_push_task = _mk_generator(MarginPushTask)
generate_random_template_lag_task = _mk_generator(TemplateLagTask)
generate_random_roc_walk_task = _mk_generator(RocWalkTask)
generate_random_ema_loss_task = _mk_generator(EmaLossTask)
generate_random_lr_decay_task = _mk_generator(LrDecayTask)
generate_random_batch_grad_task = _mk_generator(BatchGradTask)
generate_random_best_margin_task = _mk_generator(BestMarginTask)
generate_random_ctc_collapse_task = _mk_generator(CtcCollapseTask)
generate_random_relu_chain_task = _mk_generator(ReluChainTask)
generate_random_causal_pick_task = _mk_generator(CausalPickTask)
generate_random_triplet_gap_task = _mk_generator(TripletGapTask)
generate_random_beam_keep_task = _mk_generator(BeamKeepTask)
generate_random_draft_accept_task = _mk_generator(DraftAcceptTask)
generate_random_class_margin_task = _mk_generator(ClassMarginTask)
generate_random_bin_tally_task = _mk_generator(BinTallyTask)
generate_random_grad_accum_task = _mk_generator(GradAccumTask)
generate_random_skip_add_task = _mk_generator(SkipAddTask)
generate_random_online_base_task = _mk_generator(OnlineBaseTask)
generate_random_td_clip_task = _mk_generator(TdClipTask)
generate_random_count_bonus_task = _mk_generator(CountBonusTask)
generate_random_option_hold_task = _mk_generator(OptionHoldTask)
generate_random_policy_eval_task = _mk_generator(PolicyEvalTask)
generate_random_hindsight_hit_task = _mk_generator(HindsightHitTask)
generate_random_legal_greedy_task = _mk_generator(LegalGreedyTask)
generate_random_reward_machine_task = _mk_generator(RewardMachineTask)
generate_random_episode_cut_task = _mk_generator(EpisodeCutTask)
generate_random_best_reply_task = _mk_generator(BestReplyTask)
generate_random_arm_rate_task = _mk_generator(ArmRateTask)
generate_random_budget_step_task = _mk_generator(BudgetStepTask)
generate_random_done_boot_task = _mk_generator(DoneBootTask)
generate_random_greedy_gap_task = _mk_generator(GreedyGapTask)
generate_random_switch_cost_task = _mk_generator(SwitchCostTask)
generate_random_frobenius_coin_task = _mk_generator(FrobeniusCoinTask)
generate_random_bit_count_task = _mk_generator(BitCountTask)
generate_random_odd_sum_task = _mk_generator(OddSumTask)
generate_random_shadow_height_task = _mk_generator(ShadowHeightTask)
generate_random_manhattan_paths_task = _mk_generator(ManhattanPathsTask)
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
    "work_rates": generate_random_work_rates_task,
    "mixture_concentration": generate_random_mixture_concentration_task,
    "ratio_split": generate_random_ratio_split_task,
    "clock_hands": generate_random_clock_hands_task,
    "polygon_angles": generate_random_polygon_angles_task,
    "grid_diagonal": generate_random_grid_diagonal_task,
    "triangle_sides": generate_random_triangle_sides_task,
    "divisor_sum": generate_random_divisor_sum_task,
    "digital_root": generate_random_digital_root_task,
    "dice_ways": generate_random_dice_ways_task,
    "map_scale": generate_random_map_scale_task,
    "age_gap": generate_random_age_gap_task,
    "crew_work": generate_random_crew_work_task,
    "mix_chain": generate_random_mix_chain_task,
    "mod_chain": generate_random_mod_chain_task,
    "gcd_chain": generate_random_gcd_chain_task,
    "recurrence_walk": generate_random_recurrence_walk_task,
    "turtle_walk": generate_random_turtle_walk_task,
    "portal_walk": generate_random_portal_walk_task,
    "horner_eval": generate_random_horner_eval_task,
    "ledger_guard": generate_random_ledger_guard_task,
    "truck_trips": generate_random_truck_trips_task,
    "door_toggles": generate_random_door_toggles_task,
    "greedy_coins": generate_random_greedy_coins_task,
    "walk_range": generate_random_walk_range_task,
    "carry_add": generate_random_carry_add_task,
    "line_infection": generate_random_line_infection_task,
    "corridor_keys": generate_random_corridor_keys_task,
    "next_greater": generate_random_next_greater_task,
    "window_max": generate_random_window_max_task,
    "two_pointer_merge": generate_random_two_pointer_merge_task,
    "cooldown_schedule": generate_random_cooldown_schedule_task,
    "pancake_trace": generate_random_pancake_trace_task,
    "bracket_scan": generate_random_bracket_scan_task,
    "kmeans_rounds": generate_random_kmeans_rounds_task,
    "bayes_updates": generate_random_bayes_updates_task,
    "polya_urn": generate_random_polya_urn_task,
    "policy_rollout": generate_random_policy_rollout_task,
    "boost_weights": generate_random_boost_weights_task,
    "momentum_sgd": generate_random_momentum_sgd_task,
    "decision_list": generate_random_decision_list_task,
    "td_table": generate_random_td_table_task,
    "extended_euclid": generate_random_extended_euclid_task,
    "crt_chain": generate_random_crt_chain_task,
    "cf_expand": generate_random_cf_expand_task,
    "nim_sum": generate_random_nim_sum_task,
    "difference_table": generate_random_difference_table_task,
    "sandpile_path": generate_random_sandpile_path_task,
    "markov_steps": generate_random_markov_steps_task,
    "sir_ticks": generate_random_sir_ticks_task,
    "poly_div": generate_random_poly_div_task,
    "johnson_span": generate_random_johnson_span_task,
    "lights_path": generate_random_lights_path_task,
    "domino_chain": generate_random_domino_chain_task,
    "bound_scan": generate_random_bound_scan_task,
    "claim_count": generate_random_claim_count_task,
    "quorum_rise": generate_random_quorum_rise_task,
    "hat_line": generate_random_hat_line_task,
    "reagent_chain": generate_random_reagent_chain_task,
    "tax_brackets": generate_random_tax_brackets_task,
    "codon_scan": generate_random_codon_scan_task,
    "dose_schedule": generate_random_dose_schedule_task,
    "melody_walk": generate_random_melody_walk_task,
    "fifo_cost": generate_random_fifo_cost_task,
    "borda_count": generate_random_borda_count_task,
    "shift_add": generate_random_shift_add_task,
    "rally_lead": generate_random_rally_lead_task,
    "pascal_row": generate_random_pascal_row_task,
    "fraction_ops": generate_random_fraction_ops_task,
    "stern_path": generate_random_stern_path_task,
    "partition_count": generate_random_partition_count_task,
    "derange_count": generate_random_derange_count_task,
    "gauss_mul": generate_random_gauss_mul_task,
    "perm_compose": generate_random_perm_compose_task,
    "cover_span": generate_random_cover_span_task,
    "reverse_add": generate_random_reverse_add_task,
    "stream_median": generate_random_stream_median_task,
    "totient_row": generate_random_totient_row_task,
    "coprime_count": generate_random_coprime_count_task,
    "digit_div": generate_random_digit_div_task,
    "tree_depth": generate_random_tree_depth_task,
    "sign_walk": generate_random_sign_walk_task,
    "perm_rank": generate_random_perm_rank_task,
    "lcm_rise": generate_random_lcm_rise_task,
    "zigzag_row": generate_random_zigzag_row_task,
    "record_highs": generate_random_record_highs_task,
    "sum_kinds": generate_random_sum_kinds_task,
    "fib_word": generate_random_fib_word_task,
    "mode_track": generate_random_mode_track_task,
    "look_say": generate_random_look_say_task,
    "zeckendorf": generate_random_zeckendorf_task,
    "roman_value": generate_random_roman_value_task,
    "digit_stream": generate_random_digit_stream_task,
    "deque_trace": generate_random_deque_trace_task,
    "dragon_fold": generate_random_dragon_fold_task,
    "permanent": generate_random_permanent_task,
    "bead_count": generate_random_bead_count_task,
    "negabase": generate_random_negabase_task,
    "ulam_walk": generate_random_ulam_walk_task,
    "luhn_sum": generate_random_luhn_sum_task,
    "kaprekar_step": generate_random_kaprekar_step_task,
    "morton_code": generate_random_morton_code_task,
    "stock_span": generate_random_stock_span_task,
    "candy_row": generate_random_candy_row_task,
    "digit_fact": generate_random_digit_fact_task,
    "recaman": generate_random_recaman_task,
    "xor_basis": generate_random_xor_basis_task,
    "palindrome_radius": generate_random_palindrome_radius_task,
    "squarefree_row": generate_random_squarefree_row_task,
    "fenwick_sum": generate_random_fenwick_sum_task,
    "sparse_min": generate_random_sparse_min_task,
    "z_array": generate_random_z_array_task,
    "selection_swaps": generate_random_selection_swaps_task,
    "rho_cycle": generate_random_rho_cycle_task,
    "tree_times": generate_random_tree_times_task,
    "dutch_flag": generate_random_dutch_flag_task,
    "window_distinct": generate_random_window_distinct_task,
    "stable_place": generate_random_stable_place_task,
    "naive_find": generate_random_naive_find_task,
    "budget_take": generate_random_budget_take_task,
    "skip_op": generate_random_skip_op_task,
    "retry_goal": generate_random_retry_goal_task,
    "signal_edges": generate_random_signal_edges_task,
    "plan_gate": generate_random_plan_gate_task,
    "tool_pick": generate_random_tool_pick_task,
    "diff_count": generate_random_diff_count_task,
    "cell_patch": generate_random_cell_patch_task,
    "pred_scan": generate_random_pred_scan_task,
    "rate_limit": generate_random_rate_limit_task,
    "lateness": generate_random_lateness_task,
    "switch_flip": generate_random_switch_flip_task,
    "turn_signs": generate_random_turn_signs_task,
    "first_fit": generate_random_first_fit_task,
    "plurality": generate_random_plurality_task,
    "floor_run": generate_random_floor_run_task,
    "saturate_count": generate_random_saturate_count_task,
    "undo_reg": generate_random_undo_reg_task,
    "cover_point": generate_random_cover_point_task,
    "next_fit": generate_random_next_fit_task,
    "neighbor_vote": generate_random_neighbor_vote_task,
    "sgd_online": generate_random_sgd_online_task,
    "grad_clip": generate_random_grad_clip_task,
    "weight_decay": generate_random_weight_decay_task,
    "early_stop": generate_random_early_stop_task,
    "prototype_mean": generate_random_prototype_mean_task,
    "trace_decay": generate_random_trace_decay_task,
    "actor_critic": generate_random_actor_critic_task,
    "ucb_bandit": generate_random_ucb_bandit_task,
    "target_sync": generate_random_target_sync_task,
    "replay_fifo": generate_random_replay_fifo_task,
    "shape_reward": generate_random_shape_reward_task,
    "eps_schedule": generate_random_eps_schedule_task,
    "scope_lookup": generate_random_scope_lookup_task,
    "lock_log": generate_random_lock_log_task,
    "path_toll": generate_random_path_toll_task,
    "backoff_wait": generate_random_backoff_wait_task,
    "priority_run": generate_random_priority_run_task,
    "inbox_take": generate_random_inbox_take_task,
    "goal_match": generate_random_goal_match_task,
    "craft_need": generate_random_craft_need_task,
    "checkpoint_roll": generate_random_checkpoint_roll_task,
    "schema_check": generate_random_schema_check_task,
    "infix_value": generate_random_infix_value_task,
    "ballot_walk": generate_random_ballot_walk_task,
    "digit_root": generate_random_digit_root_task,
    "crt_lift": generate_random_crt_lift_task,
    "mod_order": generate_random_mod_order_task,
    "first_repeat": generate_random_first_repeat_task,
    "coupon_cover": generate_random_coupon_cover_task,
    "coin_weigh": generate_random_coin_weigh_task,
    "two_color": generate_random_two_color_task,
    "lattice_sum": generate_random_lattice_sum_task,
    "horner_mod": generate_random_horner_mod_task,
    "rational_root": generate_random_rational_root_task,
    "geom_sum": generate_random_geom_sum_task,
    "cyclo_eval": generate_random_cyclo_eval_task,
    "chebyshev_row": generate_random_chebyshev_row_task,
    "hermite_row": generate_random_hermite_row_task,
    "series_conv": generate_random_series_conv_task,
    "transport_cost": generate_random_transport_cost_task,
    "pochhammer": generate_random_pochhammer_task,
    "binom_build": generate_random_binom_build_task,
    "farey_next": generate_random_farey_next_task,
    "mobius_sum": generate_random_mobius_sum_task,
    "involution_count": generate_random_involution_count_task,
    "jacobi_row": generate_random_jacobi_row_task,
    "ruler_sum": generate_random_ruler_sum_task,
    "thue_count": generate_random_thue_count_task,
    "aliquot_walk": generate_random_aliquot_walk_task,
    "carmichael_row": generate_random_carmichael_row_task,
    "cayley_trees": generate_random_cayley_trees_task,
    "factoradic": generate_random_factoradic_task,
    "stirling_first": generate_random_stirling_first_task,
    "bell_row": generate_random_bell_row_task,
    "andre_row": generate_random_andre_row_task,
    "bernoulli_den": generate_random_bernoulli_den_task,
    "chebyshev_u": generate_random_chebyshev_u_task,
    "sigma_row": generate_random_sigma_row_task,
    "prime_omega": generate_random_prime_omega_task,
    "motzkin_row": generate_random_motzkin_row_task,
    "primorial": generate_random_primorial_task,
    "rgs_rank": generate_random_rgs_rank_task,
    "bernoulli_numer": generate_random_bernoulli_numer_task,
    "genocchi_row": generate_random_genocchi_row_task,
    "kronecker_row": generate_random_kronecker_row_task,
    "hook_length": generate_random_hook_length_task,
    "legendre_frac": generate_random_legendre_frac_task,
    "laguerre_frac": generate_random_laguerre_frac_task,
    "harmonic_frac": generate_random_harmonic_frac_task,
    "eulerian_row": generate_random_eulerian_row_task,
    "fubini_row": generate_random_fubini_row_task,
    "delannoy_row": generate_random_delannoy_row_task,
    "tau_row": generate_random_tau_row_task,
    "prime_nu": generate_random_prime_nu_task,
    "sopfr_row": generate_random_sopfr_row_task,
    "pell_row": generate_random_pell_row_task,
    "tribonacci_row": generate_random_tribonacci_row_task,
    "narayana_row": generate_random_narayana_row_task,
    "schroder_row": generate_random_schroder_row_task,
    "gaussian_bin": generate_random_gaussian_bin_task,
    "kolakoski": generate_random_kolakoski_task,
    "cantor_pair": generate_random_cantor_pair_task,
    "horn_fire": generate_random_horn_fire_task,
    "carry_row": generate_random_carry_row_task,
    "lamp_trio": generate_random_lamp_trio_task,
    "parity_sheet": generate_random_parity_sheet_task,
    "mux_index": generate_random_mux_index_task,
    "jury_veto": generate_random_jury_veto_task,
    "gate_fold": generate_random_gate_fold_task,
    "exactly_one": generate_random_exactly_one_task,
    "knave_next": generate_random_knave_next_task,
    "priority_bit": generate_random_priority_bit_task,
    "interval_merge": generate_random_interval_merge_task,
    "cycle_count": generate_random_cycle_count_task,
    "stack_perm": generate_random_stack_perm_task,
    "inversion_row": generate_random_inversion_row_task,
    "run_length": generate_random_run_length_task,
    "median_merge": generate_random_median_merge_task,
    "diag_cross": generate_random_diag_cross_task,
    "billiard_cross": generate_random_billiard_cross_task,
    "popcount_sum": generate_random_popcount_sum_task,
    "rencontres_row": generate_random_rencontres_row_task,
    "ballot_tri": generate_random_ballot_tri_task,
    "dedekind_psi": generate_random_dedekind_psi_task,
    "jordan_tot": generate_random_jordan_tot_task,
    "sylvester_row": generate_random_sylvester_row_task,
    "lucas_row": generate_random_lucas_row_task,
    "liouville_row": generate_random_liouville_row_task,
    "necklace_count": generate_random_necklace_count_task,
    "hamming_smooth": generate_random_hamming_smooth_task,
    "menage_count": generate_random_menage_count_task,
    "bracket_final": generate_random_bracket_final_task,
    "unit_prop": generate_random_unit_prop_task,
    "gf2_solve": generate_random_gf2_solve_task,
    "resolve_proof": generate_random_resolve_proof_task,
    "bool_eq": generate_random_bool_eq_task,
    "assign_check": generate_random_assign_check_task,
    "pigeon_place": generate_random_pigeon_place_task,
    "kripke_box": generate_random_kripke_box_task,
    "all_are": generate_random_all_are_task,
    "literal_clash": generate_random_literal_clash_task,
    "until_line": generate_random_until_line_task,
    "dung_ground": generate_random_dung_ground_task,
    "causal_do": generate_random_causal_do_task,
    "lukas_fold": generate_random_lukas_fold_task,
    "doctrinal": generate_random_doctrinal_task,
    "knows_line": generate_random_knows_line_task,
    "rough_set": generate_random_rough_set_task,
    "naf_fire": generate_random_naf_fire_task,
    "agenda_vote": generate_random_agenda_vote_task,
    "short_circuit": generate_random_short_circuit_task,
    "ref_count": generate_random_ref_count_task,
    "wrap_index": generate_random_wrap_index_task,
    "bit_prog": generate_random_bit_prog_task,
    "break_sum": generate_random_break_sum_task,
    "bounds_step": generate_random_bounds_step_task,
    "reg_swap": generate_random_reg_swap_task,
    "elif_pick": generate_random_elif_pick_task,
    "post_inc": generate_random_post_inc_task,
    "min_hold": generate_random_min_hold_task,
    "jump_add": generate_random_jump_add_task,
    "div_chain": generate_random_div_chain_task,
    "clamp_add": generate_random_clamp_add_task,
    "ptr_walk": generate_random_ptr_walk_task,
    "continue_sum": generate_random_continue_sum_task,
    "delay_line": generate_random_delay_line_task,
    "switch_case": generate_random_switch_case_task,
    "digit_scan": generate_random_digit_scan_task,
    "rot_nibble": generate_random_rot_nibble_task,
    "buf_len": generate_random_buf_len_task,
    "cmp_branch": generate_random_cmp_branch_task,
    "bit_set": generate_random_bit_set_task,
    "cell_write": generate_random_cell_write_task,
    "lcg_step": generate_random_lcg_step_task,
    "two_stack": generate_random_two_stack_task,
    "sorted_insert": generate_random_sorted_insert_task,
    "brace_pair": generate_random_brace_pair_task,
    "hash_probe": generate_random_hash_probe_task,
    "part_count": generate_random_part_count_task,
    "fill_forward": generate_random_fill_forward_task,
    "xor_fold": generate_random_xor_fold_task,
    "bubble_pass": generate_random_bubble_pass_task,
    "mtf_list": generate_random_mtf_list_task,
    "turnstile": generate_random_turnstile_task,
    "hamming_step": generate_random_hamming_step_task,
    "row_major": generate_random_row_major_task,
    "union_count": generate_random_union_count_task,
    "trie_node": generate_random_trie_node_task,
    "minute_add": generate_random_minute_add_task,
    "mod_accum": generate_random_mod_accum_task,
    "nfa_run": generate_random_nfa_run_task,
    "moore_run": generate_random_moore_run_task,
    "sync_run": generate_random_sync_run_task,
    "meet_run": generate_random_meet_run_task,
    "lfsr_run": generate_random_lfsr_run_task,
    "crc_rem": generate_random_crc_rem_task,
    "feistel_run": generate_random_feistel_run_task,
    "elgamal_enc": generate_random_elgamal_enc_task,
    "fact_base": generate_random_fact_base_task,
    "cas_cell": generate_random_cas_cell_task,
    "memo_call": generate_random_memo_call_task,
    "skip_fit": generate_random_skip_fit_task,
    "handoff_ask": generate_random_handoff_ask_task,
    "reject_add": generate_random_reject_add_task,
    "ref_resolve": generate_random_ref_resolve_task,
    "belief_vote": generate_random_belief_vote_task,
    "join_wait": generate_random_join_wait_task,
    "audit_sum": generate_random_audit_sum_task,
    "draw_out": generate_random_draw_out_task,
    "die_build": generate_random_die_build_task,
    "rank_stop": generate_random_rank_stop_task,
    "day_clash": generate_random_day_clash_task,
    "group_mean": generate_random_group_mean_task,
    "safe_bits": generate_random_safe_bits_task,
    "first_to": generate_random_first_to_task,
    "odds_mass": generate_random_odds_mass_task,
    "simpson_pool": generate_random_simpson_pool_task,
    "job_slack": generate_random_job_slack_task,
    "pair_vote": generate_random_pair_vote_task,
    "screen_count": generate_random_screen_count_task,
    "burn_balance": generate_random_burn_balance_task,
    "h_index": generate_random_h_index_task,
    "allele_fit": generate_random_allele_fit_task,
    "pareto_keep": generate_random_pareto_keep_task,
    "perm_order": generate_random_perm_order_task,
    "perm_conj": generate_random_perm_conj_task,
    "add_orbit": generate_random_add_orbit_task,
    "unit_mod": generate_random_unit_mod_task,
    "nil_index": generate_random_nil_index_task,
    "mod_poly": generate_random_mod_poly_task,
    "heisen_mul": generate_random_heisen_mul_task,
    "coset_rep": generate_random_coset_rep_task,
    "betti_mod": generate_random_betti_mod_task,
    "curve_add": generate_random_curve_add_task,
    "smith_inv": generate_random_smith_inv_task,
    "form_reduce": generate_random_form_reduce_task,
    "res_chain": generate_random_res_chain_task,
    "sturm_root": generate_random_sturm_root_task,
    "anf_fold": generate_random_anf_fold_task,
    "coin_wait": generate_random_coin_wait_task,
    "ruin_time": generate_random_ruin_time_task,
    "mix_count": generate_random_mix_count_task,
    "repeat_test": generate_random_repeat_test_task,
    "group_var": generate_random_group_var_task,
    "pivot_cost": generate_random_pivot_cost_task,
    "hard_attend": generate_random_hard_attend_task,
    "max_pool": generate_random_max_pool_task,
    "adam_tick": generate_random_adam_tick_task,
    "rnn_add": generate_random_rnn_add_task,
    "margin_push": generate_random_margin_push_task,
    "template_lag": generate_random_template_lag_task,
    "roc_walk": generate_random_roc_walk_task,
    "ema_loss": generate_random_ema_loss_task,
    "lr_decay": generate_random_lr_decay_task,
    "batch_grad": generate_random_batch_grad_task,
    "best_margin": generate_random_best_margin_task,
    "ctc_collapse": generate_random_ctc_collapse_task,
    "relu_chain": generate_random_relu_chain_task,
    "causal_pick": generate_random_causal_pick_task,
    "triplet_gap": generate_random_triplet_gap_task,
    "beam_keep": generate_random_beam_keep_task,
    "draft_accept": generate_random_draft_accept_task,
    "class_margin": generate_random_class_margin_task,
    "bin_tally": generate_random_bin_tally_task,
    "grad_accum": generate_random_grad_accum_task,
    "skip_add": generate_random_skip_add_task,
    "online_base": generate_random_online_base_task,
    "td_clip": generate_random_td_clip_task,
    "count_bonus": generate_random_count_bonus_task,
    "option_hold": generate_random_option_hold_task,
    "policy_eval": generate_random_policy_eval_task,
    "hindsight_hit": generate_random_hindsight_hit_task,
    "legal_greedy": generate_random_legal_greedy_task,
    "reward_machine": generate_random_reward_machine_task,
    "episode_cut": generate_random_episode_cut_task,
    "best_reply": generate_random_best_reply_task,
    "arm_rate": generate_random_arm_rate_task,
    "budget_step": generate_random_budget_step_task,
    "done_boot": generate_random_done_boot_task,
    "greedy_gap": generate_random_greedy_gap_task,
    "switch_cost": generate_random_switch_cost_task,
    "frobenius_coin": generate_random_frobenius_coin_task,
    "bit_count": generate_random_bit_count_task,
    "odd_sum": generate_random_odd_sum_task,
    "shadow_height": generate_random_shadow_height_task,
    "manhattan_paths": generate_random_manhattan_paths_task,
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
        raise ValueError(texts.t('s5', language, task_type=task_type, v1=list(ALL_TASK_GENERATORS.keys())))
    
    # Передаём параметры, которые поддерживает генератор
    return generator(language=language, detail_level=detail_level, difficulty=difficulty, **kwargs)
