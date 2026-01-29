# re_rl/tasks/math/analysis/__init__.py

"""Задачи математического анализа."""

from re_rl.tasks.math.analysis.calculus_task import CalculusTask
from re_rl.tasks.math.analysis.limits_task import LimitsTask
from re_rl.tasks.math.analysis.integral_task import IntegralTask
from re_rl.tasks.math.analysis.differential_equation_task import DifferentialEquationTask
from re_rl.tasks.math.analysis.series_task import SeriesTask
from re_rl.tasks.math.analysis.optimization_task import OptimizationTask

__all__ = [
    "CalculusTask",
    "LimitsTask",
    "IntegralTask",
    "DifferentialEquationTask",
    "SeriesTask",
    "OptimizationTask",
]
