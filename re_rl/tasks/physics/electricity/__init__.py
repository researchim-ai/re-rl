# re_rl/tasks/physics/electricity/__init__.py

"""Задачи по электричеству."""

from re_rl.tasks.physics.electricity.circuits_task import CircuitsTask
from re_rl.tasks.physics.electricity.electrostatics_task import ElectrostaticsTask
from re_rl.tasks.physics.electricity.capacitors_task import CapacitorsTask
from re_rl.tasks.physics.electricity.electromagnetic_induction_task import ElectromagneticInductionTask
from re_rl.tasks.physics.electricity.ac_circuits_task import ACCircuitsTask
from re_rl.tasks.physics.electricity.rc_circuits_task import RCCircuitsTask

__all__ = [
    "CircuitsTask",
    "ElectrostaticsTask",
    "CapacitorsTask",
    "ElectromagneticInductionTask",
    "ACCircuitsTask",
    "RCCircuitsTask",
]
