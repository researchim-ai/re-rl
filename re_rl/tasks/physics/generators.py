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

# Квантовая механика
from re_rl.tasks.physics.quantum.quantum_task import QuantumTask

# Ядерная физика
from re_rl.tasks.physics.nuclear.nuclear_task import NuclearTask

# Магнетизм
from re_rl.tasks.physics.magnetism.magnetism_task import MagnetismTask

# Специальная теория относительности
from re_rl.tasks.physics.relativity.relativity_task import RelativityTask

# Колебания
from re_rl.tasks.physics.oscillations.oscillations_task import OscillationsTask

# Гидростатика
from re_rl.tasks.physics.fluids.fluids_task import FluidsTask

# Астрофизика
from re_rl.tasks.physics.astrophysics.astrophysics_task import AstrophysicsTask


##################################################
# Генераторы механики
##################################################

def generate_random_kinematics_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5,
                                    output_format: str = "text"):
    return KinematicsTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               output_format=output_format)

def generate_random_dynamics_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5,
                                  output_format: str = "text"):
    return DynamicsTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty)

def generate_random_energy_task(task_type: str = None, language: str = "ru",
                                detail_level: int = 3, difficulty: int = 5,
                                output_format: str = "text"):
    return EnergyTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty)

def generate_random_momentum_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5,
                                  output_format: str = "text"):
    return MomentumTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы электричества
##################################################

def generate_random_circuits_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5):
    return CircuitsTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty)

def generate_random_electrostatics_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return ElectrostaticsTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty)

def generate_random_capacitors_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5):
    return CapacitorsTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы термодинамики
##################################################

def generate_random_gas_laws_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5):
    return GasLawsTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)

def generate_random_heat_transfer_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5):
    return HeatTransferTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы волн и оптики
##################################################

def generate_random_waves_task(task_type: str = None, language: str = "ru",
                               detail_level: int = 3, difficulty: int = 5):
    return WavesTask.generate_random_task(task_type=task_type, language=language,
                                          detail_level=detail_level, difficulty=difficulty)

def generate_random_optics_task(task_type: str = None, language: str = "ru",
                                detail_level: int = 3, difficulty: int = 5):
    return OpticsTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы квантовой механики
##################################################

def generate_random_quantum_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5):
    return QuantumTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы ядерной физики
##################################################

def generate_random_nuclear_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5):
    return NuclearTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы магнетизма
##################################################

def generate_random_magnetism_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5):
    return MagnetismTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы СТО
##################################################

def generate_random_relativity_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5):
    return RelativityTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы колебаний
##################################################

def generate_random_oscillations_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5):
    return OscillationsTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы гидростатики
##################################################

def generate_random_fluids_task(task_type: str = None, language: str = "ru",
                                detail_level: int = 3, difficulty: int = 5):
    return FluidsTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы астрофизики
##################################################

def generate_random_astrophysics_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5):
    return AstrophysicsTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty)


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
    # Квантовая механика
    "quantum": generate_random_quantum_task,
    # Ядерная физика
    "nuclear": generate_random_nuclear_task,
    # Магнетизм
    "magnetism": generate_random_magnetism_task,
    # СТО
    "relativity": generate_random_relativity_task,
    # Колебания
    "oscillations": generate_random_oscillations_task,
    # Гидростатика
    "fluids": generate_random_fluids_task,
    # Астрофизика
    "astrophysics": generate_random_astrophysics_task,
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
        task_name: Название задачи (kinematics, dynamics, circuits, quantum, ...).
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
