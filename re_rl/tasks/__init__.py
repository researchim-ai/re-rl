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
from re_rl.tasks.registry import registry

__all__ = [
    # Базовые классы
    "BaseTask",
    "BaseMathTask",
    "DifficultyMixin",
    
    # Арифметика
    "ArithmeticTask",
    "ArithmeticConfig",
    
    # Математические задачи
    "LinearTask",
    "QuadraticTask",
    "CubicTask",
    "SystemLinearTask",
    "ExponentialTask",
    "LogarithmicTask",
    "CalculusTask",
    
    # Логические задачи
    "GraphTask",
    "AnalogicalTask",
    "ContradictionTask",
    "KnightsKnavesTask",
    "FutoshikiTask",
    
    # Прочие
    "UrnProbabilityTask",
    "TextStatsTask",
    
    # Реестр
    "registry",
]
