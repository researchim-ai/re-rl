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

# Специальная теория относительности
from re_rl.tasks.physics.relativity.relativity_task import RelativityTask

# Колебания
from re_rl.tasks.physics.oscillations.oscillations_task import OscillationsTask

# Гидростатика
from re_rl.tasks.physics.fluids.fluids_task import FluidsTask

# Астрофизика
from re_rl.tasks.physics.astrophysics.astrophysics_task import AstrophysicsTask

# Измерения и анализ
from re_rl.tasks.physics.measurements.dimensional_analysis_task import DimensionalAnalysisTask
from re_rl.tasks.physics.measurements.error_propagation_task import ErrorPropagationTask
from re_rl.tasks.physics.measurements.unit_conversion_task import UnitConversionTask

# Новая волна физических задач
from re_rl.tasks.physics.mechanics.statics_equilibrium_task import StaticsEquilibriumTask
from re_rl.tasks.physics.mechanics.circular_dynamics_task import CircularDynamicsTask
from re_rl.tasks.physics.mechanics.rolling_motion_task import RollingMotionTask
from re_rl.tasks.physics.thermodynamics.kinetic_theory_task import KineticTheoryTask
from re_rl.tasks.physics.thermodynamics.thermal_expansion_task import ThermalExpansionTask
from re_rl.tasks.physics.thermodynamics.blackbody_radiation_task import BlackbodyRadiationTask
from re_rl.tasks.physics.waves.standing_waves_task import StandingWavesTask
from re_rl.tasks.physics.waves.sound_intensity_task import SoundIntensityTask
from re_rl.tasks.physics.waves.beats_task import BeatsTask
from re_rl.tasks.physics.electricity.kirchhoff_laws_task import KirchhoffLawsTask
from re_rl.tasks.physics.electricity.rl_circuits_task import RLCircuitsTask
from re_rl.tasks.physics.electricity.gauss_law_task import GaussLawTask
from re_rl.tasks.physics.electricity.transformer_task import TransformerTask
from re_rl.tasks.physics.relativity.relativistic_energy_task import RelativisticEnergyTask
from re_rl.tasks.physics.relativity.velocity_addition_task import VelocityAdditionTask
from re_rl.tasks.physics.quantum.radiation_pressure_task import RadiationPressureTask

# Новейшая волна физических задач
from re_rl.tasks.physics.mechanics.elasticity_task import ElasticityTask
from re_rl.tasks.physics.mechanics.terminal_velocity_task import TerminalVelocityTask
from re_rl.tasks.physics.fluids.surface_tension_task import SurfaceTensionTask
from re_rl.tasks.physics.electricity.wheatstone_bridge_task import WheatstoneBridgeTask
from re_rl.tasks.physics.thermodynamics.gas_work_task import GasWorkTask
from re_rl.tasks.physics.thermodynamics.mean_free_path_task import MeanFreePathTask
from re_rl.tasks.physics.quantum.pair_production_task import PairProductionTask

# Масштабируемые (многошаговые) физические задачи
from re_rl.tasks.physics.networks.series_parallel_task import SeriesParallelNetworkTask
from re_rl.tasks.physics.thermodynamics.pv_cycle_task import PVCycleTask
from re_rl.tasks.physics.mechanics.elastic_chain_task import ElasticChainTask
from re_rl.tasks.physics.waves.abcd_optics_task import ABCDOpticsTask
from re_rl.tasks.physics.mechanics.composite_inertia_task import CompositeInertiaTask
from re_rl.tasks.physics.thermodynamics.calorimetry_mix_task import CalorimetryMixTask


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

def generate_random_projectile_motion_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return ProjectileMotionTask(task_type=task_type, language=language,
                                detail_level=detail_level, difficulty=difficulty)

def generate_random_rotational_dynamics_task(task_type: str = None, language: str = "ru",
                                             detail_level: int = 3, difficulty: int = 5):
    return RotationalDynamicsTask(task_type=task_type, language=language,
                                  detail_level=detail_level, difficulty=difficulty)

def generate_random_center_of_mass_task(language: str = "ru", detail_level: int = 3, difficulty: int = 5):
    return CenterOfMassTask(language=language, detail_level=detail_level, difficulty=difficulty)

def generate_random_atwood_machine_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return AtwoodMachineTask(task_type=task_type, language=language,
                             detail_level=detail_level, difficulty=difficulty)

def generate_random_inclined_plane_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return InclinedPlaneTask(task_type=task_type, language=language,
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

def generate_random_electromagnetic_induction_task(task_type: str = None, language: str = "ru",
                                                   detail_level: int = 3, difficulty: int = 5):
    return ElectromagneticInductionTask(task_type=task_type, language=language,
                                        detail_level=detail_level, difficulty=difficulty)

def generate_random_ac_circuits_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return ACCircuitsTask(task_type=task_type, language=language,
                          detail_level=detail_level, difficulty=difficulty)

def generate_random_rc_circuits_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return RCCircuitsTask(task_type=task_type, language=language,
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

def generate_random_thermodynamic_cycles_task(task_type: str = None, language: str = "ru",
                                              detail_level: int = 3, difficulty: int = 5):
    return ThermodynamicCyclesTask(task_type=task_type, language=language,
                                   detail_level=detail_level, difficulty=difficulty)

def generate_random_entropy_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5):
    return EntropyTask(task_type=task_type, language=language,
                       detail_level=detail_level, difficulty=difficulty)

def generate_random_phase_transitions_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return PhaseTransitionsTask(task_type=task_type, language=language,
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

def generate_random_doppler_effect_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return DopplerEffectTask(task_type=task_type, language=language,
                             detail_level=detail_level, difficulty=difficulty)

def generate_random_interference_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5):
    return InterferenceTask(task_type=task_type, language=language,
                            detail_level=detail_level, difficulty=difficulty)

def generate_random_diffraction_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return DiffractionTask(task_type=task_type, language=language,
                           detail_level=detail_level, difficulty=difficulty)

def generate_random_polarization_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5):
    return PolarizationTask(task_type=task_type, language=language,
                            detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы квантовой механики
##################################################

def generate_random_quantum_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5):
    return QuantumTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)

def generate_random_bohr_model_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5):
    return BohrModelTask(task_type=task_type, language=language,
                         detail_level=detail_level, difficulty=difficulty)

def generate_random_de_broglie_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5):
    return DeBroglieTask(task_type=task_type, language=language,
                         detail_level=detail_level, difficulty=difficulty)

def generate_random_uncertainty_principle_task(task_type: str = None, language: str = "ru",
                                               detail_level: int = 3, difficulty: int = 5):
    return UncertaintyPrincipleTask(task_type=task_type, language=language,
                                    detail_level=detail_level, difficulty=difficulty)

def generate_random_radioactive_decay_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return RadioactiveDecayTask(task_type=task_type, language=language,
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

def generate_random_magnetic_force_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return MagneticForceTask(task_type=task_type, language=language,
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
# Генераторы измерений и анализа
##################################################

def generate_random_dimensional_analysis_task(task_type: str = None, language: str = "ru",
                                              detail_level: int = 3, difficulty: int = 5):
    return DimensionalAnalysisTask(task_type=task_type, language=language,
                                   detail_level=detail_level, difficulty=difficulty)

def generate_random_error_propagation_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return ErrorPropagationTask(task_type=task_type, language=language,
                                detail_level=detail_level, difficulty=difficulty)

def generate_random_unit_conversion_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5):
    return UnitConversionTask(task_type=task_type, language=language,
                              detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы новой волны физических задач
##################################################

def generate_random_statics_equilibrium_task(task_type: str = None, language: str = "ru",
                                              detail_level: int = 3, difficulty: int = 5):
    return StaticsEquilibriumTask.generate_random_task(task_type=task_type, language=language,
                                                       detail_level=detail_level, difficulty=difficulty)

def generate_random_circular_dynamics_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return CircularDynamicsTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_rolling_motion_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return RollingMotionTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty)

def generate_random_kinetic_theory_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return KineticTheoryTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty)

def generate_random_thermal_expansion_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return ThermalExpansionTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_blackbody_radiation_task(task_type: str = None, language: str = "ru",
                                             detail_level: int = 3, difficulty: int = 5):
    return BlackbodyRadiationTask.generate_random_task(task_type=task_type, language=language,
                                                       detail_level=detail_level, difficulty=difficulty)

def generate_random_standing_waves_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return StandingWavesTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty)

def generate_random_sound_intensity_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5):
    return SoundIntensityTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty)

def generate_random_beats_task(task_type: str = None, language: str = "ru",
                               detail_level: int = 3, difficulty: int = 5):
    return BeatsTask.generate_random_task(task_type=task_type, language=language,
                                          detail_level=detail_level, difficulty=difficulty)

def generate_random_kirchhoff_laws_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return KirchhoffLawsTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty)

def generate_random_rl_circuits_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return RLCircuitsTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty)

def generate_random_gauss_law_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5):
    return GaussLawTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty)

def generate_random_transformer_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return TransformerTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty)

def generate_random_relativistic_energy_task(task_type: str = None, language: str = "ru",
                                             detail_level: int = 3, difficulty: int = 5):
    return RelativisticEnergyTask.generate_random_task(task_type=task_type, language=language,
                                                       detail_level=detail_level, difficulty=difficulty)

def generate_random_velocity_addition_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return VelocityAdditionTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_radiation_pressure_task(task_type: str = None, language: str = "ru",
                                            detail_level: int = 3, difficulty: int = 5):
    return RadiationPressureTask.generate_random_task(task_type=task_type, language=language,
                                                      detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы новейшей волны физических задач
##################################################

def generate_random_elasticity_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return ElasticityTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty)

def generate_random_terminal_velocity_task(task_type: str = None, language: str = "ru",
                                            detail_level: int = 3, difficulty: int = 5):
    return TerminalVelocityTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_surface_tension_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5):
    return SurfaceTensionTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty)

def generate_random_wheatstone_bridge_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return WheatstoneBridgeTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_gas_work_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5):
    return GasWorkTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)

def generate_random_mean_free_path_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5):
    return MeanFreePathTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty)

def generate_random_pair_production_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5):
    return PairProductionTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty)


##################################################
# Генераторы масштабируемых физических задач
##################################################

def generate_random_series_parallel_network_task(task_type: str = None, language: str = "ru",
                                                  detail_level: int = 3, difficulty: int = 5):
    return SeriesParallelNetworkTask.generate_random_task(task_type=task_type, language=language,
                                                          detail_level=detail_level, difficulty=difficulty)

def generate_random_pv_cycle_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5):
    return PVCycleTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty)

def generate_random_elastic_chain_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5):
    return ElasticChainTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty)

def generate_random_abcd_optics_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5):
    return ABCDOpticsTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty)

def generate_random_composite_inertia_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5):
    return CompositeInertiaTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty)

def generate_random_calorimetry_mix_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5):
    return CalorimetryMixTask.generate_random_task(task_type=task_type, language=language,
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
    "projectile_motion": generate_random_projectile_motion_task,
    "rotational_dynamics": generate_random_rotational_dynamics_task,
    "center_of_mass": generate_random_center_of_mass_task,
    "atwood_machine": generate_random_atwood_machine_task,
    "inclined_plane": generate_random_inclined_plane_task,
    # Электричество
    "circuits": generate_random_circuits_task,
    "electrostatics": generate_random_electrostatics_task,
    "capacitors": generate_random_capacitors_task,
    "electromagnetic_induction": generate_random_electromagnetic_induction_task,
    "ac_circuits": generate_random_ac_circuits_task,
    "rc_circuits": generate_random_rc_circuits_task,
    # Термодинамика
    "gas_laws": generate_random_gas_laws_task,
    "heat_transfer": generate_random_heat_transfer_task,
    "thermodynamic_cycles": generate_random_thermodynamic_cycles_task,
    "entropy": generate_random_entropy_task,
    "phase_transitions": generate_random_phase_transitions_task,
    # Волны и оптика
    "waves": generate_random_waves_task,
    "optics": generate_random_optics_task,
    "doppler_effect": generate_random_doppler_effect_task,
    "interference": generate_random_interference_task,
    "diffraction": generate_random_diffraction_task,
    "polarization": generate_random_polarization_task,
    # Квантовая механика
    "quantum": generate_random_quantum_task,
    "bohr_model": generate_random_bohr_model_task,
    "de_broglie": generate_random_de_broglie_task,
    "uncertainty_principle": generate_random_uncertainty_principle_task,
    "radioactive_decay": generate_random_radioactive_decay_task,
    # Ядерная физика
    "nuclear": generate_random_nuclear_task,
    # Магнетизм
    "magnetism": generate_random_magnetism_task,
    "magnetic_force": generate_random_magnetic_force_task,
    # СТО
    "relativity": generate_random_relativity_task,
    # Колебания
    "oscillations": generate_random_oscillations_task,
    # Гидростатика
    "fluids": generate_random_fluids_task,
    # Астрофизика
    "astrophysics": generate_random_astrophysics_task,
    # Измерения и анализ
    "dimensional_analysis": generate_random_dimensional_analysis_task,
    "error_propagation": generate_random_error_propagation_task,
    "unit_conversion": generate_random_unit_conversion_task,
    # Новая волна: механика
    "statics_equilibrium": generate_random_statics_equilibrium_task,
    "circular_dynamics": generate_random_circular_dynamics_task,
    "rolling_motion": generate_random_rolling_motion_task,
    # Новая волна: термодинамика
    "kinetic_theory": generate_random_kinetic_theory_task,
    "thermal_expansion": generate_random_thermal_expansion_task,
    "blackbody_radiation": generate_random_blackbody_radiation_task,
    # Новая волна: волны и звук
    "standing_waves": generate_random_standing_waves_task,
    "sound_intensity": generate_random_sound_intensity_task,
    "beats": generate_random_beats_task,
    # Новая волна: электричество и магнетизм
    "kirchhoff_laws": generate_random_kirchhoff_laws_task,
    "rl_circuits": generate_random_rl_circuits_task,
    "gauss_law": generate_random_gauss_law_task,
    "transformer": generate_random_transformer_task,
    # Новая волна: современная физика
    "relativistic_energy": generate_random_relativistic_energy_task,
    "velocity_addition": generate_random_velocity_addition_task,
    "radiation_pressure": generate_random_radiation_pressure_task,
    # Новейшая волна: механика и гидродинамика
    "elasticity": generate_random_elasticity_task,
    "terminal_velocity": generate_random_terminal_velocity_task,
    "surface_tension": generate_random_surface_tension_task,
    # Новейшая волна: электричество
    "wheatstone_bridge": generate_random_wheatstone_bridge_task,
    # Новейшая волна: термодинамика
    "gas_work": generate_random_gas_work_task,
    "mean_free_path": generate_random_mean_free_path_task,
    # Новейшая волна: современная физика
    "pair_production": generate_random_pair_production_task,
    # Масштабируемые многошаговые задачи
    "series_parallel_network": generate_random_series_parallel_network_task,
    "pv_cycle": generate_random_pv_cycle_task,
    "elastic_chain": generate_random_elastic_chain_task,
    "abcd_optics": generate_random_abcd_optics_task,
    "composite_inertia": generate_random_composite_inertia_task,
    "calorimetry_mix": generate_random_calorimetry_mix_task,
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
