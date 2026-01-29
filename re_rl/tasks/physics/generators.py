# re_rl/tasks/physics/generators.py

"""
Генераторы для физических задач.
"""

import random
from typing import Optional

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


##################################################
# Генераторы механики
##################################################

def generate_random_kinematics_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу по кинематике."""
    return KinematicsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_dynamics_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу по динамике."""
    return DynamicsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_energy_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на энергию."""
    return EnergyTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_momentum_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на импульс."""
    return MomentumTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# Генераторы электричества
##################################################

def generate_random_circuits_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на электрические цепи."""
    return CircuitsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_electrostatics_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу по электростатике."""
    return ElectrostaticsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_capacitors_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на конденсаторы."""
    return CapacitorsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# Генераторы термодинамики
##################################################

def generate_random_gas_laws_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на газовые законы."""
    return GasLawsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_heat_transfer_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на теплопередачу."""
    return HeatTransferTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# Генераторы волн и оптики
##################################################

def generate_random_waves_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу на волны."""
    return WavesTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


def generate_random_optics_task(
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """Генерирует случайную задачу по оптике."""
    return OpticsTask.generate_random_task(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )


##################################################
# Словарь всех генераторов физических задач
##################################################

ALL_PHYSICS_TASK_GENERATORS = {
    # Механика
    "kinematics": generate_random_kinematics_task,
    "dynamics": generate_random_dynamics_task,
    "energy": generate_random_energy_task,
    "momentum": generate_random_momentum_task,
    # Электричество
    "circuits": generate_random_circuits_task,
    "electrostatics": generate_random_electrostatics_task,
    "capacitors": generate_random_capacitors_task,
    # Термодинамика
    "gas_laws": generate_random_gas_laws_task,
    "heat_transfer": generate_random_heat_transfer_task,
    # Волны и оптика
    "waves": generate_random_waves_task,
    "optics": generate_random_optics_task,
}


def generate_random_physics_task(
    task_name: str = None,
    task_type: str = None,
    language: str = "ru",
    detail_level: int = 3,
    difficulty: int = 5
):
    """
    Генерирует случайную физическую задачу.
    
    Args:
        task_name: Название задачи (kinematics, dynamics, circuits, ...).
                   Если None, выбирается случайно.
        task_type: Подтип задачи (зависит от task_name)
        language: Язык ('ru' или 'en')
        detail_level: Уровень детализации решения
        difficulty: Сложность от 1 до 10
    
    Returns:
        Экземпляр задачи
    """
    if task_name is None:
        task_name = random.choice(list(ALL_PHYSICS_TASK_GENERATORS.keys()))
    
    generator = ALL_PHYSICS_TASK_GENERATORS.get(task_name)
    if generator is None:
        raise ValueError(f"Unknown physics task: {task_name}. "
                        f"Available: {list(ALL_PHYSICS_TASK_GENERATORS.keys())}")
    
    return generator(
        task_type=task_type,
        language=language,
        detail_level=detail_level,
        difficulty=difficulty
    )
