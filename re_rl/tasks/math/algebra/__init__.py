# re_rl/tasks/math/algebra/__init__.py

"""Алгебраические задачи."""

from re_rl.tasks.math.algebra.linear_task import LinearTask
from re_rl.tasks.math.algebra.quadratic_task import QuadraticTask
from re_rl.tasks.math.algebra.cubic_task import CubicTask
from re_rl.tasks.math.algebra.system_linear_task import SystemLinearTask
from re_rl.tasks.math.algebra.exponential_task import ExponentialTask
from re_rl.tasks.math.algebra.logarithmic_task import LogarithmicTask
from re_rl.tasks.math.algebra.inequality_task import InequalityTask

__all__ = [
    "LinearTask",
    "QuadraticTask",
    "CubicTask",
    "SystemLinearTask",
    "ExponentialTask",
    "LogarithmicTask",
    "InequalityTask",
]
