# re_rl/tasks/physics/__init__.py

"""
Физические задачи.

Категории:
- mechanics: механика (кинематика, динамика, энергия, импульс)
- electricity: электричество (цепи, электростатика, конденсаторы)
- thermodynamics: термодинамика (газовые законы, теплопередача)
- waves: волны и оптика
- quantum: квантовая механика
- nuclear: ядерная физика
- magnetism: магнетизм
- relativity: специальная теория относительности
- oscillations: колебания
- fluids: гидростатика и гидродинамика
- astrophysics: астрофизика
"""

# Механика
from re_rl.tasks.physics.mechanics.kinematics_task import KinematicsTask
from re_rl.tasks.physics.mechanics.dynamics_task import DynamicsTask
from re_rl.tasks.physics.mechanics.energy_task import EnergyTask
from re_rl.tasks.physics.mechanics.momentum_task import MomentumTask
from re_rl.tasks.physics.mechanics.projectile_motion_task import ProjectileMotionTask
from re_rl.tasks.physics.mechanics.rotational_dynamics_task import RotationalDynamicsTask
from re_rl.tasks.physics.mechanics.center_of_mass_task import CenterOfMassTask
from re_rl.tasks.physics.mechanics.atwood_machine_task import AtwoodMachineTask
from re_rl.tasks.physics.mechanics.inclined_plane_task import InclinedPlaneTask

# Электричество
from re_rl.tasks.physics.electricity.circuits_task import CircuitsTask
from re_rl.tasks.physics.electricity.electrostatics_task import ElectrostaticsTask
from re_rl.tasks.physics.electricity.capacitors_task import CapacitorsTask
from re_rl.tasks.physics.electricity.electromagnetic_induction_task import ElectromagneticInductionTask
from re_rl.tasks.physics.electricity.ac_circuits_task import ACCircuitsTask
from re_rl.tasks.physics.electricity.rc_circuits_task import RCCircuitsTask

# Термодинамика
from re_rl.tasks.physics.thermodynamics.gas_laws_task import GasLawsTask
from re_rl.tasks.physics.thermodynamics.heat_transfer_task import HeatTransferTask
from re_rl.tasks.physics.thermodynamics.thermodynamic_cycles_task import ThermodynamicCyclesTask
from re_rl.tasks.physics.thermodynamics.entropy_task import EntropyTask
from re_rl.tasks.physics.thermodynamics.phase_transitions_task import PhaseTransitionsTask

# Волны и оптика
from re_rl.tasks.physics.waves.waves_task import WavesTask
from re_rl.tasks.physics.waves.optics_task import OpticsTask
from re_rl.tasks.physics.waves.doppler_effect_task import DopplerEffectTask
from re_rl.tasks.physics.waves.interference_task import InterferenceTask
from re_rl.tasks.physics.waves.diffraction_task import DiffractionTask
from re_rl.tasks.physics.waves.polarization_task import PolarizationTask

# Квантовая механика
from re_rl.tasks.physics.quantum.quantum_task import QuantumTask
from re_rl.tasks.physics.quantum.bohr_model_task import BohrModelTask
from re_rl.tasks.physics.quantum.de_broglie_task import DeBroglieTask
from re_rl.tasks.physics.quantum.uncertainty_principle_task import UncertaintyPrincipleTask
from re_rl.tasks.physics.quantum.radioactive_decay_task import RadioactiveDecayTask

# Ядерная физика
from re_rl.tasks.physics.nuclear.nuclear_task import NuclearTask

# Магнетизм
from re_rl.tasks.physics.magnetism.magnetism_task import MagnetismTask
from re_rl.tasks.physics.magnetism.magnetic_force_task import MagneticForceTask

# Измерения
from re_rl.tasks.physics.measurements.dimensional_analysis_task import DimensionalAnalysisTask
from re_rl.tasks.physics.measurements.error_propagation_task import ErrorPropagationTask
from re_rl.tasks.physics.measurements.unit_conversion_task import UnitConversionTask

# СТО
from re_rl.tasks.physics.relativity.relativity_task import RelativityTask

# Колебания
from re_rl.tasks.physics.oscillations.oscillations_task import OscillationsTask

# Гидростатика
from re_rl.tasks.physics.fluids.fluids_task import FluidsTask

# Астрофизика
from re_rl.tasks.physics.astrophysics.astrophysics_task import AstrophysicsTask

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
    generate_random_quantum_task,
    generate_random_nuclear_task,
    generate_random_magnetism_task,
    generate_random_relativity_task,
    generate_random_oscillations_task,
    generate_random_fluids_task,
    generate_random_astrophysics_task,
    ALL_PHYSICS_TASK_GENERATORS,
)

__all__ = [
    # Механика
    "KinematicsTask",
    "DynamicsTask",
    "EnergyTask",
    "MomentumTask",
    "ProjectileMotionTask",
    "RotationalDynamicsTask",
    "CenterOfMassTask",
    "AtwoodMachineTask",
    "InclinedPlaneTask",
    # Электричество
    "CircuitsTask",
    "ElectrostaticsTask",
    "CapacitorsTask",
    "ElectromagneticInductionTask",
    "ACCircuitsTask",
    "RCCircuitsTask",
    # Термодинамика
    "GasLawsTask",
    "HeatTransferTask",
    "ThermodynamicCyclesTask",
    "EntropyTask",
    "PhaseTransitionsTask",
    # Волны
    "WavesTask",
    "OpticsTask",
    "DopplerEffectTask",
    "InterferenceTask",
    "DiffractionTask",
    "PolarizationTask",
    # Квантовая механика
    "QuantumTask",
    "BohrModelTask",
    "DeBroglieTask",
    "UncertaintyPrincipleTask",
    "RadioactiveDecayTask",
    # Ядерная физика
    "NuclearTask",
    # Магнетизм
    "MagnetismTask",
    "MagneticForceTask",
    # СТО
    "RelativityTask",
    # Колебания
    "OscillationsTask",
    # Гидростатика
    "FluidsTask",
    # Астрофизика
    "AstrophysicsTask",
    # Измерения
    "DimensionalAnalysisTask",
    "ErrorPropagationTask",
    "UnitConversionTask",
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
    "generate_random_quantum_task",
    "generate_random_nuclear_task",
    "generate_random_magnetism_task",
    "generate_random_relativity_task",
    "generate_random_oscillations_task",
    "generate_random_fluids_task",
    "generate_random_astrophysics_task",
    "ALL_PHYSICS_TASK_GENERATORS",
]
