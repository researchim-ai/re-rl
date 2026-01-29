# re_rl/tasks/__init__.py

"""
Модуль задач для генерации датасетов.

Структура:
- math/: математические задачи
- physics/: физические задачи
"""

# Базовые классы (остаются в корне tasks/)
from re_rl.tasks.base_task import BaseTask, BaseMathTask, DifficultyMixin
from re_rl.tasks.registry import registry

# ============================================================================
# МАТЕМАТИЧЕСКИЕ ЗАДАЧИ (из math/)
# ============================================================================

# Алгебра
from re_rl.tasks.math.algebra.linear_task import LinearTask
from re_rl.tasks.math.algebra.quadratic_task import QuadraticTask
from re_rl.tasks.math.algebra.cubic_task import CubicTask
from re_rl.tasks.math.algebra.system_linear_task import SystemLinearTask
from re_rl.tasks.math.algebra.exponential_task import ExponentialTask
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask
from re_rl.tasks.math.algebra.inequality_task import InequalityTask

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

# Прикладная математика
from re_rl.tasks.math.applied.financial_math_task import FinancialMathTask
from re_rl.tasks.math.applied.arithmetic_task import ArithmeticTask, ArithmeticConfig

# Логика
from re_rl.tasks.math.logic.contradiction_task import ContradictionTask
from re_rl.tasks.math.logic.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.math.logic.futoshiki_task import FutoshikiTask
from re_rl.tasks.math.logic.analogical_task import AnalogicalTask
from re_rl.tasks.math.logic.text_stats_task import TextStatsTask

# ============================================================================
# ФИЗИЧЕСКИЕ ЗАДАЧИ (из physics/)
# ============================================================================

# Механика
from re_rl.tasks.physics.mechanics.kinematics_task import KinematicsTask
from re_rl.tasks.physics.mechanics.dynamics_task import DynamicsTask
from re_rl.tasks.physics.mechanics.energy_task import EnergyTask
from re_rl.tasks.physics.mechanics.momentum_task import MomentumTask

# Электричество
from re_rl.tasks.physics.electricity.circuits_task import CircuitsTask
from re_rl.tasks.physics.electricity.electrostatics_task import ElectrostaticsTask
from re_rl.tasks.physics.electricity.capacitors_task import CapacitorsTask

# Термодинамика
from re_rl.tasks.physics.thermodynamics.gas_laws_task import GasLawsTask
from re_rl.tasks.physics.thermodynamics.heat_transfer_task import HeatTransferTask

# Волны и оптика
from re_rl.tasks.physics.waves.waves_task import WavesTask
from re_rl.tasks.physics.waves.optics_task import OpticsTask

# Физические утилиты
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS, get_constant
from re_rl.tasks.physics.units import convert_units, format_with_units

# Генераторы физики
from re_rl.tasks.physics.generators import (
    generate_random_physics_task,
    generate_random_kinematics_task,
    generate_random_dynamics_task,
    generate_random_energy_task,
    generate_random_momentum_task,
    generate_random_circuits_task,
    generate_random_electrostatics_task,
    generate_random_capacitors_task,
    generate_random_gas_laws_task,
    generate_random_heat_transfer_task,
    generate_random_waves_task,
    generate_random_optics_task,
    ALL_PHYSICS_TASK_GENERATORS,
)

# ============================================================================
# ГЕНЕРАТОРЫ МАТЕМАТИКИ
# ============================================================================
from re_rl.tasks.generators import (
    # Math generators
    generate_random_task,
    generate_random_arithmetic_task,
    generate_random_linear_task,
    generate_random_quadratic_task,
    generate_random_cubic_task,
    generate_random_exponential_task,
    generate_random_logarithmic_task,
    generate_random_calculus_task,
    generate_random_contradiction_task,
    generate_random_knights_knaves_task,
    generate_random_futoshiki_task,
    generate_random_urn_probability_task,
    generate_random_text_stats_task,
    generate_random_graph_task,
    generate_random_system_linear_task,
    generate_random_analogical_task,
    generate_random_group_theory_task,
    generate_random_category_theory_task,
    generate_random_number_theory_task,
    generate_random_combinatorics_task,
    generate_random_sequence_task,
    generate_random_geometry_task,
    generate_random_matrix_task,
    generate_random_trigonometry_task,
    generate_random_inequality_task,
    generate_random_complex_number_task,
    generate_random_limits_task,
    generate_random_set_logic_task,
    generate_random_statistics_task,
    generate_random_integral_task,
    generate_random_differential_equation_task,
    generate_random_optimization_task,
    generate_random_vector_3d_task,
    generate_random_financial_math_task,
    generate_random_series_task,
    ALL_TASK_GENERATORS,
)

__all__ = [
    # Базовые классы
    "BaseTask",
    "BaseMathTask",
    "DifficultyMixin",
    "registry",
    
    # Алгебра
    "LinearTask",
    "QuadraticTask", 
    "CubicTask",
    "SystemLinearTask",
    "ExponentialTask",
    "LogarithmicTask",
    "InequalityTask",
    
    # Анализ
    "CalculusTask",
    "LimitsTask",
    "IntegralTask",
    "DifferentialEquationTask",
    "SeriesTask",
    "OptimizationTask",
    
    # Геометрия
    "GeometryTask",
    "TrigonometryTask",
    "Vector3DTask",
    
    # Линейная алгебра
    "MatrixTask",
    "ComplexNumberTask",
    
    # Дискретная математика
    "NumberTheoryTask",
    "CombinatoricsTask",
    "SequenceTask",
    "SetLogicTask",
    "GraphTask",
    
    # Абстрактная алгебра
    "GroupTheoryTask",
    "CategoryTheoryTask",
    
    # Вероятность
    "UrnProbabilityTask",
    "StatisticsTask",
    
    # Прикладная
    "FinancialMathTask",
    "ArithmeticTask",
    "ArithmeticConfig",
    
    # Логика
    "ContradictionTask",
    "KnightsKnavesTask",
    "FutoshikiTask",
    "AnalogicalTask",
    "TextStatsTask",
    
    # Физика - Механика
    "KinematicsTask",
    "DynamicsTask",
    "EnergyTask",
    "MomentumTask",
    
    # Физика - Электричество
    "CircuitsTask",
    "ElectrostaticsTask",
    "CapacitorsTask",
    
    # Физика - Термодинамика
    "GasLawsTask",
    "HeatTransferTask",
    
    # Физика - Волны
    "WavesTask",
    "OpticsTask",
    
    # Физические утилиты
    "PHYSICS_CONSTANTS",
    "get_constant",
    "convert_units",
    "format_with_units",
    
    # Генераторы математики
    "generate_random_task",
    "generate_random_arithmetic_task",
    "generate_random_linear_task",
    "generate_random_quadratic_task",
    "generate_random_cubic_task",
    "generate_random_exponential_task",
    "generate_random_logarithmic_task",
    "generate_random_calculus_task",
    "generate_random_contradiction_task",
    "generate_random_knights_knaves_task",
    "generate_random_futoshiki_task",
    "generate_random_urn_probability_task",
    "generate_random_text_stats_task",
    "generate_random_graph_task",
    "generate_random_system_linear_task",
    "generate_random_analogical_task",
    "generate_random_group_theory_task",
    "generate_random_category_theory_task",
    "generate_random_number_theory_task",
    "generate_random_combinatorics_task",
    "generate_random_sequence_task",
    "generate_random_geometry_task",
    "generate_random_matrix_task",
    "generate_random_trigonometry_task",
    "generate_random_inequality_task",
    "generate_random_complex_number_task",
    "generate_random_limits_task",
    "generate_random_set_logic_task",
    "generate_random_statistics_task",
    "generate_random_integral_task",
    "generate_random_differential_equation_task",
    "generate_random_optimization_task",
    "generate_random_vector_3d_task",
    "generate_random_financial_math_task",
    "generate_random_series_task",
    "ALL_TASK_GENERATORS",
    
    # Генераторы физики
    "generate_random_physics_task",
    "generate_random_kinematics_task",
    "generate_random_dynamics_task",
    "generate_random_energy_task",
    "generate_random_momentum_task",
    "generate_random_circuits_task",
    "generate_random_electrostatics_task",
    "generate_random_capacitors_task",
    "generate_random_gas_laws_task",
    "generate_random_heat_transfer_task",
    "generate_random_waves_task",
    "generate_random_optics_task",
    "ALL_PHYSICS_TASK_GENERATORS",
]
