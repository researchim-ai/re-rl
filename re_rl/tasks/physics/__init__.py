# re_rl/tasks/physics/__init__.py

"""
Физические задачи.

Категории:
- mechanics: механика (кинематика, динамика, энергия, импульс)
- electricity: электричество (цепи, электростатика, конденсаторы)
- thermodynamics: термодинамика (газовые законы, теплопередача)
- waves: волны и оптика
"""

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

# Утилиты
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS, get_constant, format_constant_info
from re_rl.tasks.physics.units import convert_units, format_with_units, auto_scale_unit

# Генераторы
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

__all__ = [
    # Механика
    "KinematicsTask",
    "DynamicsTask",
    "EnergyTask",
    "MomentumTask",
    # Электричество
    "CircuitsTask",
    "ElectrostaticsTask",
    "CapacitorsTask",
    # Термодинамика
    "GasLawsTask",
    "HeatTransferTask",
    # Волны
    "WavesTask",
    "OpticsTask",
    # Утилиты
    "PHYSICS_CONSTANTS",
    "get_constant",
    "format_constant_info",
    "convert_units",
    "format_with_units",
    "auto_scale_unit",
    # Генераторы
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
