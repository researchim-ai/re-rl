# re_rl/tasks/physics/electricity/__init__.py

"""Задачи по электричеству."""

from re_rl.tasks.physics.electricity.circuits_task import CircuitsTask
from re_rl.tasks.physics.electricity.electrostatics_task import ElectrostaticsTask
from re_rl.tasks.physics.electricity.capacitors_task import CapacitorsTask

__all__ = [
    "CircuitsTask",
    "ElectrostaticsTask",
    "CapacitorsTask",
]
