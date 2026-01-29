# re_rl/tasks/physics/mechanics/__init__.py

"""Задачи по механике."""

from re_rl.tasks.physics.mechanics.kinematics_task import KinematicsTask
from re_rl.tasks.physics.mechanics.dynamics_task import DynamicsTask
from re_rl.tasks.physics.mechanics.energy_task import EnergyTask
from re_rl.tasks.physics.mechanics.momentum_task import MomentumTask
from re_rl.tasks.physics.mechanics.projectile_motion_task import ProjectileMotionTask
from re_rl.tasks.physics.mechanics.rotational_dynamics_task import RotationalDynamicsTask
from re_rl.tasks.physics.mechanics.center_of_mass_task import CenterOfMassTask
from re_rl.tasks.physics.mechanics.atwood_machine_task import AtwoodMachineTask
from re_rl.tasks.physics.mechanics.inclined_plane_task import InclinedPlaneTask

__all__ = [
    "KinematicsTask",
    "DynamicsTask",
    "EnergyTask",
    "MomentumTask",
    "ProjectileMotionTask",
    "RotationalDynamicsTask",
    "CenterOfMassTask",
    "AtwoodMachineTask",
    "InclinedPlaneTask",
]
