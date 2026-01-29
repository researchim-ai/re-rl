# re_rl/tasks/physics/mechanics/__init__.py

"""Задачи по механике."""

from re_rl.tasks.physics.mechanics.kinematics_task import KinematicsTask
from re_rl.tasks.physics.mechanics.dynamics_task import DynamicsTask
from re_rl.tasks.physics.mechanics.energy_task import EnergyTask
from re_rl.tasks.physics.mechanics.momentum_task import MomentumTask

__all__ = [
    "KinematicsTask",
    "DynamicsTask",
    "EnergyTask",
    "MomentumTask",
]
