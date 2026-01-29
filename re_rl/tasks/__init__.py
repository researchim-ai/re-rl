# re_rl/tasks/__init__.py

"""
Модуль задач для генерации датасетов.

Экспортирует основные классы задач и систему сложности.
"""

from re_rl.tasks.base_task import BaseTask, BaseMathTask, DifficultyMixin
from re_rl.tasks.arithmetic_task import ArithmeticTask, ArithmeticConfig
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.system_linear_task import SystemLinearTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.analogical_task import AnalogicalTask
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.futoshiki_task import FutoshikiTask
from re_rl.tasks.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.text_stats_task import TextStatsTask
from re_rl.tasks.group_theory_task import GroupTheoryTask
from re_rl.tasks.category_theory_task import CategoryTheoryTask
from re_rl.tasks.registry import registry

# Новые задачи
from re_rl.tasks.number_theory_task import NumberTheoryTask
from re_rl.tasks.combinatorics_task import CombinatoricsTask
from re_rl.tasks.sequence_task import SequenceTask
from re_rl.tasks.geometry_task import GeometryTask
from re_rl.tasks.matrix_task import MatrixTask
from re_rl.tasks.trigonometry_task import TrigonometryTask
from re_rl.tasks.inequality_task import InequalityTask
from re_rl.tasks.complex_number_task import ComplexNumberTask
from re_rl.tasks.limits_task import LimitsTask
from re_rl.tasks.set_logic_task import SetLogicTask

# Генераторы
from re_rl.tasks.generators import (
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
    ALL_TASK_GENERATORS,
)

__all__ = [
    # Базовые классы
    "BaseTask",
    "BaseMathTask",
    "DifficultyMixin",
    
    # Арифметика
    "ArithmeticTask",
    "ArithmeticConfig",
    
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
    
    # Теория чисел и комбинаторика
    "NumberTheoryTask",
    "CombinatoricsTask",
    "SequenceTask",
    
    # Геометрия и тригонометрия
    "GeometryTask",
    "TrigonometryTask",
    
    # Линейная алгебра
    "MatrixTask",
    "ComplexNumberTask",
    
    # Множества и логика
    "SetLogicTask",
    
    # Абстрактная алгебра
    "GroupTheoryTask",
    "CategoryTheoryTask",
    
    # Логические задачи
    "GraphTask",
    "AnalogicalTask",
    "ContradictionTask",
    "KnightsKnavesTask",
    "FutoshikiTask",
    
    # Вероятность и статистика
    "UrnProbabilityTask",
    "TextStatsTask",
    
    # Генераторы
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
    "ALL_TASK_GENERATORS",
    
    # Реестр
    "registry",
]
