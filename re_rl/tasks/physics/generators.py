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
from re_rl.tasks.physics.thermodynamics.adiabatic_task import AdiabaticTask
from re_rl.tasks.physics.mechanics.ballistic_pendulum_task import BallisticPendulumTask
from re_rl.tasks.physics.mechanics.restitution_task import RestitutionTask
from re_rl.tasks.physics.mechanics.meeting_motion_task import MeetingMotionTask
from re_rl.tasks.physics.electricity.internal_resistance_task import InternalResistanceTask
from re_rl.tasks.physics.electricity.lc_oscillator_task import LCOscillatorTask
from re_rl.tasks.physics.astrophysics.parallax_task import ParallaxTask
from re_rl.tasks.physics.quantum.half_life_task import HalfLifeStepsTask
from re_rl.tasks.physics.thermodynamics.fourier_task import FourierConductionTask
from re_rl.tasks.physics.mechanics.spring_energy_task import SpringEnergyTask
from re_rl.tasks.physics.mechanics.efficiency_task import EfficiencyTask
from re_rl.tasks.physics.mechanics.relative_velocity_task import RelativeVelocityTask
from re_rl.tasks.physics.oscillations.pendulum_ratio_task import PendulumRatioTask
from re_rl.tasks.physics.waves.wave_relation_task import WaveRelationTask
from re_rl.tasks.physics.thermodynamics.sensible_heat_task import SensibleHeatTask
from re_rl.tasks.physics.electricity.resistor_pair_task import ResistorPairTask
from re_rl.tasks.physics.mechanics.reduced_mass_task import ReducedMassTask
from re_rl.tasks.physics.magnetism.cyclotron_task import CyclotronTask
from re_rl.tasks.physics.astrophysics.redshift_task import RedshiftTask
from re_rl.tasks.physics.relativity.rational_gamma_task import RationalGammaTask
from re_rl.tasks.physics.thermodynamics.stefan_ratio_task import StefanRatioTask
from re_rl.tasks.physics.electricity.inductor_energy_task import InductorEnergyTask
from re_rl.tasks.physics.waves.doppler_shift_task import DopplerShiftTask
from re_rl.tasks.physics.astrophysics.hubble_task import HubbleTask
from re_rl.tasks.physics.mechanics.free_fall_task import FreeFallTask
from re_rl.tasks.physics.mechanics.hooke_law_task import HookeLawTask
from re_rl.tasks.physics.measurements.density_task import DensityTask
from re_rl.tasks.physics.mechanics.average_speed_task import AverageSpeedTask
from re_rl.tasks.physics.mechanics.lever_balance_task import LeverBalanceTask
from re_rl.tasks.physics.waves.echo_delay_task import EchoDelayTask
from re_rl.tasks.physics.electricity.joule_heat_task import JouleHeatTask
from re_rl.tasks.physics.mechanics.boat_current_task import BoatCurrentTask
from re_rl.tasks.physics.mechanics.gear_ratio_task import GearRatioTask
from re_rl.tasks.physics.waves.mirror_glance_task import MirrorGlanceTask
from re_rl.tasks.physics.mechanics.gear_train_task import GearTrainTask
from re_rl.tasks.physics.mechanics.relay_time_task import RelayTimeTask
from re_rl.tasks.physics.electricity.voltage_divider_task import VoltageDividerTask
from re_rl.tasks.physics.mechanics.spring_series_task import SpringSeriesTask
from re_rl.tasks.physics.mechanics.block_stack_task import BlockStackTask
from re_rl.tasks.physics.mechanics.sticking_chain_task import StickingChainTask
from re_rl.tasks.physics.waves.lens_stack_task import LensStackTask
from re_rl.tasks.physics.fluids.cascade_tanks_task import CascadeTanksTask
from re_rl.tasks.physics.networks.network_reduce_task import NetworkReduceTask
from re_rl.tasks.physics.quantum.decay_generations_task import DecayGenerationsTask
from re_rl.tasks.physics.mechanics.bounce_heights_task import BounceHeightsTask
from re_rl.tasks.physics.electricity.charge_redistribute_task import ChargeRedistributeTask
from re_rl.tasks.physics.relativity.boost_chain_task import BoostChainTask
from re_rl.tasks.physics.mechanics.weighing_trace_task import WeighingTraceTask
from re_rl.tasks.physics.electricity.switch_net_task import SwitchNetTask
from re_rl.tasks.physics.mechanics.billiard_box_task import BilliardBoxTask
from re_rl.tasks.physics.mechanics.mobile_torque_task import MobileTorqueTask
from re_rl.tasks.physics.mechanics.traffic_light_task import TrafficLightTask
from re_rl.tasks.physics.measurements.drop_cross_task import DropCrossTask
from re_rl.tasks.physics.mechanics.ternary_balance_task import TernaryBalanceTask
from re_rl.tasks.physics.mechanics.siding_counter_task import SidingCounterTask
from re_rl.tasks.physics.mechanics.motion_segments_task import MotionSegmentsTask
from re_rl.tasks.physics.mechanics.slope_run_task import SlopeRunTask
from re_rl.tasks.physics.mechanics.echo_bounce_task import EchoBounceTask
from re_rl.tasks.physics.mechanics.fall_ticks_task import FallTicksTask
from re_rl.tasks.physics.mechanics.friction_slide_task import FrictionSlideTask
from re_rl.tasks.physics.thermodynamics.heat_mix_task import HeatMixTask
from re_rl.tasks.physics.thermodynamics.heat_rod_task import HeatRodTask
from re_rl.tasks.physics.waves.wave_row_task import WaveRowTask
from re_rl.tasks.physics.electricity.leak_charge_task import LeakChargeTask
from re_rl.tasks.physics.electricity.resistor_ladder_task import ResistorLadderTask
from re_rl.tasks.physics.waves.doppler_chain_task import DopplerChainTask
from re_rl.tasks.physics.fluids.float_load_task import FloatLoadTask
from re_rl.tasks.physics.thermodynamics.melt_heat_task import MeltHeatTask
from re_rl.tasks.physics.mechanics.throw_ticks_task import ThrowTicksTask
from re_rl.tasks.physics.mechanics.impulse_run_task import ImpulseRunTask
from re_rl.tasks.physics.mechanics.beam_load_task import BeamLoadTask
from re_rl.tasks.physics.mechanics.mass_shift_task import MassShiftTask
from re_rl.tasks.physics.mechanics.spring_join_task import SpringJoinTask
from re_rl.tasks.physics.waves.optic_path_task import OpticPathTask
from re_rl.tasks.physics.waves.pulse_meet_task import PulseMeetTask
from re_rl.tasks.physics.thermodynamics.cool_ticks_task import CoolTicksTask
from re_rl.tasks.physics.electricity.series_cap_task import SeriesCapTask
from re_rl.tasks.physics.fluids.column_pressure_task import ColumnPressureTask
from re_rl.tasks.physics.mechanics.cradle_hit_task import CradleHitTask
from re_rl.tasks.physics.quantum.photon_eject_task import PhotonEjectTask
from re_rl.tasks.physics.astrophysics.orbit_years_task import OrbitYearsTask
from re_rl.tasks.physics.waves.grating_order_task import GratingOrderTask
from re_rl.tasks.physics.magnetism.wire_force_task import WireForceTask
from re_rl.tasks.physics.astrophysics.escape_speed_task import EscapeSpeedTask
from re_rl.tasks.physics.waves.harmonic_nodes_task import HarmonicNodesTask
from re_rl.tasks.physics.waves.snell_shift_task import SnellShiftTask
from re_rl.tasks.physics.thermodynamics.heat_steps_task import HeatStepsTask
from re_rl.tasks.physics.fluids.hydraulic_lift_task import HydraulicLiftTask
from re_rl.tasks.physics.mechanics.euler_drift_task import EulerDriftTask
from re_rl.tasks.physics.mechanics.verlet_push_task import VerletPushTask
from re_rl.tasks.physics.mechanics.drag_coast_task import DragCoastTask
from re_rl.tasks.physics.mechanics.spring_pair_task import SpringPairTask
from re_rl.tasks.physics.mechanics.swing_map_task import SwingMapTask
from re_rl.tasks.physics.electricity.poisson_row_task import PoissonRowTask
from re_rl.tasks.physics.quantum.hydro_line_task import HydroLineTask
from re_rl.tasks.physics.mechanics.force_work_task import ForceWorkTask
from re_rl.tasks.physics.mechanics.rocket_burn_task import RocketBurnTask
from re_rl.tasks.physics.mechanics.projectile_tick_task import ProjectileTickTask
from re_rl.tasks.physics.electricity.lc_tick_task import LcTickTask
from re_rl.tasks.physics.waves.polar_stack_task import PolarStackTask
from re_rl.tasks.physics.fluids.upwind_row_task import UpwindRowTask
from re_rl.tasks.physics.quantum.branch_decay_task import BranchDecayTask
from re_rl.tasks.physics.thermodynamics.ising_pass_task import IsingPassTask
from re_rl.tasks.physics.thermodynamics.flow_mix_task import FlowMixTask
from re_rl.tasks.physics.measurements.box_scope_task import BoxScopeTask
from re_rl.tasks.physics.measurements.spike_cut_task import SpikeCutTask
from re_rl.tasks.physics.measurements.twin_box_task import TwinBoxTask
from re_rl.tasks.physics.measurements.peak_hold_task import PeakHoldTask
from re_rl.tasks.physics.electricity.crack_close_task import CrackCloseTask
from re_rl.tasks.physics.electricity.source_dist_task import SourceDistTask
from re_rl.tasks.physics.electricity.slope_field_task import SlopeFieldTask
from re_rl.tasks.physics.electricity.charge_run_task import ChargeRunTask
from re_rl.tasks.physics.thermodynamics.heun_cool_task import HeunCoolTask
from re_rl.tasks.physics.thermodynamics.log_growth_task import LogGrowthTask
from re_rl.tasks.physics.mechanics.energy_drift_task import EnergyDriftTask
from re_rl.tasks.physics.mechanics.pid_track_task import PidTrackTask
from re_rl.tasks.physics.mechanics.drive_osc_task import DriveOscTask
from re_rl.tasks.physics.fluids.two_tank_task import TwoTankTask
from re_rl.tasks.physics.measurements.dose_decay_task import DoseDecayTask
from re_rl.tasks.physics.measurements.wrap_ring_task import WrapRingTask
from re_rl.tasks.physics.measurements.age_flow_task import AgeFlowTask
from re_rl.tasks.physics.quantum.rotor_drop_task import RotorDropTask
from re_rl.tasks.physics.quantum.box_jump_task import BoxJumpTask
from re_rl.tasks.physics.quantum.ho_jump_task import HoJumpTask
from re_rl.tasks.physics.quantum.rovib_line_task import RovibLineTask
from re_rl.tasks.physics.quantum.zeeman_line_task import ZeemanLineTask
from re_rl.tasks.physics.quantum.qnum_ok_task import QnumOkTask
from re_rl.tasks.physics.quantum.shell_fill_task import ShellFillTask
from re_rl.tasks.physics.quantum.level_deg_task import LevelDegTask
from re_rl.tasks.physics.quantum.path_amp_task import PathAmpTask
from re_rl.tasks.physics.quantum.franck_hertz_task import FranckHertzTask
from re_rl.tasks.physics.quantum.bond_order_task import BondOrderTask
from re_rl.tasks.physics.quantum.shoot_psi_task import ShootPsiTask
from re_rl.tasks.physics.quantum.expect_h_task import ExpectHTask
from re_rl.tasks.physics.quantum.sch_defect_task import SchDefectTask
from re_rl.tasks.physics.quantum.split_energy_task import SplitEnergyTask
from re_rl.tasks.physics.quantum.tdse_step_task import TdseStepTask
from re_rl.tasks.physics.quantum.prob_flow_task import ProbFlowTask
from re_rl.tasks.physics.quantum.trial_gap_task import TrialGapTask
from re_rl.tasks.physics.quantum.qwalk_line_task import QwalkLineTask
from re_rl.tasks.physics.quantum.mz_port_task import MzPortTask
from re_rl.tasks.physics.quantum.bound_sign_task import BoundSignTask
from re_rl.tasks.physics.quantum.ladder_down_task import LadderDownTask
from re_rl.tasks.physics.quantum.ground_iter_task import GroundIterTask
from re_rl.tasks.physics.quantum.spin_add_task import SpinAddTask
from re_rl.tasks.physics.quantum.reduce_rho_task import ReduceRhoTask
from re_rl.tasks.physics.quantum.barrier_amp_task import BarrierAmpTask
from re_rl.tasks.physics.quantum.perturb_sum_task import PerturbSumTask
from re_rl.tasks.physics.electricity.yee_line_task import YeeLineTask
from re_rl.tasks.physics.thermodynamics.shock_jump_task import ShockJumpTask
from re_rl.tasks.physics.thermodynamics.gas_path_task import GasPathTask
from re_rl.tasks.physics.fluids.pipe_flow_task import PipeFlowTask
from re_rl.tasks.physics.thermodynamics.stiff_cool_task import StiffCoolTask
from re_rl.tasks.physics.thermodynamics.heat_back_task import HeatBackTask
from re_rl.tasks.physics.thermodynamics.adiab_row_task import AdiabRowTask
from re_rl.tasks.physics.mechanics.com_frac_task import ComFracTask
from re_rl.tasks.physics.mechanics.axis_add_task import AxisAddTask
from re_rl.tasks.physics.mechanics.stick_line_task import StickLineTask
from re_rl.tasks.physics.electricity.cap_spark_task import CapSparkTask
from re_rl.tasks.physics.electricity.line_force_task import LineForceTask
from re_rl.tasks.physics.astrophysics.kepler_row_task import KeplerRowTask
from re_rl.tasks.physics.electricity.path_green_task import PathGreenTask
from re_rl.tasks.physics.mechanics.burst_split_task import BurstSplitTask
from re_rl.tasks.physics.mechanics.knock_line_task import KnockLineTask
from re_rl.tasks.physics.thermodynamics.first_heat_task import FirstHeatTask
from re_rl.tasks.physics.waves.focus_row_task import FocusRowTask


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

def generate_random_adiabatic_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return AdiabaticTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_ballistic_pendulum_task(task_type: str = None, language: str = "ru",
                                            detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BallisticPendulumTask.generate_random_task(task_type=task_type, language=language,
                                                      detail_level=detail_level, difficulty=difficulty,
                                                      **kwargs)

def generate_random_restitution_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RestitutionTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_meeting_motion_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MeetingMotionTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_internal_resistance_task(task_type: str = None, language: str = "ru",
                                             detail_level: int = 3, difficulty: int = 5, **kwargs):
    return InternalResistanceTask.generate_random_task(task_type=task_type, language=language,
                                                       detail_level=detail_level, difficulty=difficulty,
                                                       **kwargs)

def generate_random_lc_oscillator_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LCOscillatorTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_stellar_parallax_task(task_type: str = None, language: str = "ru",
                                          detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ParallaxTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_half_life_steps_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HalfLifeStepsTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_fourier_conduction_task(task_type: str = None, language: str = "ru",
                                            detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FourierConductionTask.generate_random_task(task_type=task_type, language=language,
                                                      detail_level=detail_level, difficulty=difficulty,
                                                      **kwargs)

def generate_random_spring_energy_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpringEnergyTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_mechanical_efficiency_task(task_type: str = None, language: str = "ru",
                                               detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EfficiencyTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_relative_velocity_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RelativeVelocityTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty,
                                                     **kwargs)

def generate_random_pendulum_ratio_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PendulumRatioTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_wave_relation_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return WaveRelationTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_sensible_heat_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SensibleHeatTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_resistor_pair_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ResistorPairTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_reduced_mass_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ReducedMassTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_cyclotron_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CyclotronTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_spectral_redshift_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RedshiftTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_rational_gamma_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RationalGammaTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_stefan_ratio_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return StefanRatioTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_inductor_energy_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return InductorEnergyTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_doppler_shift_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DopplerShiftTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_hubble_law_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HubbleTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty,
                                           **kwargs)

def generate_random_free_fall_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FreeFallTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_hooke_law_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HookeLawTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_density_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DensityTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_average_speed_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return AverageSpeedTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_lever_balance_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LeverBalanceTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_echo_delay_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EchoDelayTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_joule_heat_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return JouleHeatTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_boat_current_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BoatCurrentTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_gear_ratio_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return GearRatioTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_mirror_glance_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MirrorGlanceTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_gear_train_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return GearTrainTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_relay_time_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RelayTimeTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_voltage_divider_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return VoltageDividerTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_spring_series_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpringSeriesTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_block_stack_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BlockStackTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_sticking_chain_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return StickingChainTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_lens_stack_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LensStackTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_cascade_tanks_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CascadeTanksTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_network_reduce_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return NetworkReduceTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_decay_generations_task(task_type: str = None, language: str = "ru",
                                           detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DecayGenerationsTask.generate_random_task(task_type=task_type, language=language,
                                                     detail_level=detail_level, difficulty=difficulty,
                                                     **kwargs)

def generate_random_bounce_heights_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BounceHeightsTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_charge_redistribute_task(task_type: str = None, language: str = "ru",
                                             detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ChargeRedistributeTask.generate_random_task(task_type=task_type, language=language,
                                                       detail_level=detail_level, difficulty=difficulty,
                                                       **kwargs)

def generate_random_boost_chain_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BoostChainTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_weighing_trace_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return WeighingTraceTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_switch_net_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SwitchNetTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_billiard_box_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BilliardBoxTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_mobile_torque_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MobileTorqueTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_traffic_light_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TrafficLightTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_drop_cross_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DropCrossTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_ternary_balance_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TernaryBalanceTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_siding_counter_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SidingCounterTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_motion_segments_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MotionSegmentsTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_slope_run_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SlopeRunTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_echo_bounce_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EchoBounceTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_fall_ticks_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FallTicksTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_friction_slide_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FrictionSlideTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_heat_mix_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HeatMixTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_heat_rod_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HeatRodTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_wave_row_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return WaveRowTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_leak_charge_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LeakChargeTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_resistor_ladder_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ResistorLadderTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_doppler_chain_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DopplerChainTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_float_load_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FloatLoadTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_throw_ticks_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ThrowTicksTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_impulse_run_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ImpulseRunTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_beam_load_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BeamLoadTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_mass_shift_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MassShiftTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_spring_join_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpringJoinTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_optic_path_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return OpticPathTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_pulse_meet_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PulseMeetTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_cool_ticks_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CoolTicksTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_series_cap_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SeriesCapTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_cradle_hit_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CradleHitTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_photon_eject_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PhotonEjectTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_orbit_years_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return OrbitYearsTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_grating_order_task(task_type: str = None, language: str = "ru",
                                       detail_level: int = 3, difficulty: int = 5, **kwargs):
    return GratingOrderTask.generate_random_task(task_type=task_type, language=language,
                                                 detail_level=detail_level, difficulty=difficulty,
                                                 **kwargs)

def generate_random_wire_force_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return WireForceTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_escape_speed_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EscapeSpeedTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_harmonic_nodes_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HarmonicNodesTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_snell_shift_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SnellShiftTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_heat_steps_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HeatStepsTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_hydraulic_lift_task(task_type: str = None, language: str = "ru",
                                        detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HydraulicLiftTask.generate_random_task(task_type=task_type, language=language,
                                                  detail_level=detail_level, difficulty=difficulty,
                                                  **kwargs)

def generate_random_euler_drift_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EulerDriftTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_verlet_push_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return VerletPushTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_drag_coast_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DragCoastTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_spring_pair_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpringPairTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_swing_map_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SwingMapTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_poisson_row_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PoissonRowTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_hydro_line_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HydroLineTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_force_work_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ForceWorkTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_rocket_burn_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RocketBurnTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_projectile_tick_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ProjectileTickTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_lc_tick_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LcTickTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty,
                                           **kwargs)

def generate_random_polar_stack_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PolarStackTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_upwind_row_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return UpwindRowTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_branch_decay_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BranchDecayTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_ising_pass_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return IsingPassTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_flow_mix_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FlowMixTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_box_scope_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BoxScopeTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_spike_cut_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpikeCutTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_twin_box_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TwinBoxTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_peak_hold_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PeakHoldTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_crack_close_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CrackCloseTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_source_dist_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SourceDistTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_slope_field_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SlopeFieldTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_charge_run_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ChargeRunTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_heun_cool_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HeunCoolTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_log_growth_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LogGrowthTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_energy_drift_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return EnergyDriftTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_pid_track_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PidTrackTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_drive_osc_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DriveOscTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_two_tank_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TwoTankTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_dose_decay_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return DoseDecayTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_wrap_ring_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return WrapRingTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_age_flow_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return AgeFlowTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_rotor_drop_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RotorDropTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_box_jump_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BoxJumpTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_ho_jump_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HoJumpTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty,
                                           **kwargs)

def generate_random_rovib_line_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return RovibLineTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_zeeman_line_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ZeemanLineTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_qnum_ok_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return QnumOkTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty,
                                           **kwargs)

def generate_random_shell_fill_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ShellFillTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_level_deg_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LevelDegTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_path_amp_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PathAmpTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_franck_hertz_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FranckHertzTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_bond_order_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BondOrderTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_shoot_psi_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ShootPsiTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_expect_h_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ExpectHTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_sch_defect_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SchDefectTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_split_energy_task(task_type: str = None, language: str = "ru",
                                      detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SplitEnergyTask.generate_random_task(task_type=task_type, language=language,
                                                detail_level=detail_level, difficulty=difficulty,
                                                **kwargs)

def generate_random_tdse_step_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TdseStepTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_prob_flow_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ProbFlowTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_trial_gap_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return TrialGapTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_qwalk_line_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return QwalkLineTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_mz_port_task(task_type: str = None, language: str = "ru",
                                 detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MzPortTask.generate_random_task(task_type=task_type, language=language,
                                           detail_level=detail_level, difficulty=difficulty,
                                           **kwargs)

def generate_random_bound_sign_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BoundSignTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_ladder_down_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LadderDownTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_ground_iter_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return GroundIterTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_spin_add_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return SpinAddTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_reduce_rho_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ReduceRhoTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_barrier_amp_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BarrierAmpTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_perturb_sum_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PerturbSumTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_yee_line_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return YeeLineTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_shock_jump_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ShockJumpTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_gas_path_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return GasPathTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_pipe_flow_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PipeFlowTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_stiff_cool_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return StiffCoolTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_heat_back_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return HeatBackTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_adiab_row_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return AdiabRowTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_com_frac_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ComFracTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_axis_add_task(task_type: str = None, language: str = "ru",
                                  detail_level: int = 3, difficulty: int = 5, **kwargs):
    return AxisAddTask.generate_random_task(task_type=task_type, language=language,
                                            detail_level=detail_level, difficulty=difficulty,
                                            **kwargs)

def generate_random_stick_line_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return StickLineTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_cap_spark_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return CapSparkTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_line_force_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return LineForceTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_kepler_row_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return KeplerRowTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_path_green_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return PathGreenTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_burst_split_task(task_type: str = None, language: str = "ru",
                                     detail_level: int = 3, difficulty: int = 5, **kwargs):
    return BurstSplitTask.generate_random_task(task_type=task_type, language=language,
                                               detail_level=detail_level, difficulty=difficulty,
                                               **kwargs)

def generate_random_knock_line_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return KnockLineTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_first_heat_task(task_type: str = None, language: str = "ru",
                                    detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FirstHeatTask.generate_random_task(task_type=task_type, language=language,
                                              detail_level=detail_level, difficulty=difficulty,
                                              **kwargs)

def generate_random_focus_row_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return FocusRowTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

def generate_random_column_pressure_task(task_type: str = None, language: str = "ru",
                                         detail_level: int = 3, difficulty: int = 5, **kwargs):
    return ColumnPressureTask.generate_random_task(task_type=task_type, language=language,
                                                   detail_level=detail_level, difficulty=difficulty,
                                                   **kwargs)

def generate_random_melt_heat_task(task_type: str = None, language: str = "ru",
                                   detail_level: int = 3, difficulty: int = 5, **kwargs):
    return MeltHeatTask.generate_random_task(task_type=task_type, language=language,
                                             detail_level=detail_level, difficulty=difficulty,
                                             **kwargs)

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
    "adiabatic": generate_random_adiabatic_task,
    "ballistic_pendulum": generate_random_ballistic_pendulum_task,
    "restitution": generate_random_restitution_task,
    "meeting_motion": generate_random_meeting_motion_task,
    "internal_resistance": generate_random_internal_resistance_task,
    "lc_oscillator": generate_random_lc_oscillator_task,
    "stellar_parallax": generate_random_stellar_parallax_task,
    "half_life_steps": generate_random_half_life_steps_task,
    "fourier_conduction": generate_random_fourier_conduction_task,
    "spring_energy": generate_random_spring_energy_task,
    "mechanical_efficiency": generate_random_mechanical_efficiency_task,
    "relative_velocity": generate_random_relative_velocity_task,
    "pendulum_ratio": generate_random_pendulum_ratio_task,
    "wave_relation": generate_random_wave_relation_task,
    "sensible_heat": generate_random_sensible_heat_task,
    "resistor_pair": generate_random_resistor_pair_task,
    "reduced_mass": generate_random_reduced_mass_task,
    "cyclotron": generate_random_cyclotron_task,
    "spectral_redshift": generate_random_spectral_redshift_task,
    "rational_gamma": generate_random_rational_gamma_task,
    "stefan_ratio": generate_random_stefan_ratio_task,
    "inductor_energy": generate_random_inductor_energy_task,
    "doppler_shift": generate_random_doppler_shift_task,
    "hubble_law": generate_random_hubble_law_task,
    "free_fall": generate_random_free_fall_task,
    "hooke_law": generate_random_hooke_law_task,
    "density": generate_random_density_task,
    "average_speed": generate_random_average_speed_task,
    "lever_balance": generate_random_lever_balance_task,
    "echo_delay": generate_random_echo_delay_task,
    "joule_heat": generate_random_joule_heat_task,
    "boat_current": generate_random_boat_current_task,
    "gear_ratio": generate_random_gear_ratio_task,
    "mirror_glance": generate_random_mirror_glance_task,
    "gear_train": generate_random_gear_train_task,
    "relay_time": generate_random_relay_time_task,
    "voltage_divider": generate_random_voltage_divider_task,
    "spring_series": generate_random_spring_series_task,
    "block_stack": generate_random_block_stack_task,
    "sticking_chain": generate_random_sticking_chain_task,
    "lens_stack": generate_random_lens_stack_task,
    "cascade_tanks": generate_random_cascade_tanks_task,
    "network_reduce": generate_random_network_reduce_task,
    "decay_generations": generate_random_decay_generations_task,
    "bounce_heights": generate_random_bounce_heights_task,
    "charge_redistribute": generate_random_charge_redistribute_task,
    "boost_chain": generate_random_boost_chain_task,
    "weighing_trace": generate_random_weighing_trace_task,
    "switch_net": generate_random_switch_net_task,
    "billiard_box": generate_random_billiard_box_task,
    "mobile_torque": generate_random_mobile_torque_task,
    "traffic_light": generate_random_traffic_light_task,
    "drop_cross": generate_random_drop_cross_task,
    "ternary_balance": generate_random_ternary_balance_task,
    "siding_counter": generate_random_siding_counter_task,
    "motion_segments": generate_random_motion_segments_task,
    "slope_run": generate_random_slope_run_task,
    "echo_bounce": generate_random_echo_bounce_task,
    "fall_ticks": generate_random_fall_ticks_task,
    "friction_slide": generate_random_friction_slide_task,
    "heat_mix": generate_random_heat_mix_task,
    "heat_rod": generate_random_heat_rod_task,
    "wave_row": generate_random_wave_row_task,
    "leak_charge": generate_random_leak_charge_task,
    "resistor_ladder": generate_random_resistor_ladder_task,
    "doppler_chain": generate_random_doppler_chain_task,
    "float_load": generate_random_float_load_task,
    "melt_heat": generate_random_melt_heat_task,
    "throw_ticks": generate_random_throw_ticks_task,
    "impulse_run": generate_random_impulse_run_task,
    "beam_load": generate_random_beam_load_task,
    "mass_shift": generate_random_mass_shift_task,
    "spring_join": generate_random_spring_join_task,
    "optic_path": generate_random_optic_path_task,
    "pulse_meet": generate_random_pulse_meet_task,
    "cool_ticks": generate_random_cool_ticks_task,
    "series_cap": generate_random_series_cap_task,
    "column_pressure": generate_random_column_pressure_task,
    "cradle_hit": generate_random_cradle_hit_task,
    "photon_eject": generate_random_photon_eject_task,
    "orbit_years": generate_random_orbit_years_task,
    "grating_order": generate_random_grating_order_task,
    "wire_force": generate_random_wire_force_task,
    "escape_speed": generate_random_escape_speed_task,
    "harmonic_nodes": generate_random_harmonic_nodes_task,
    "snell_shift": generate_random_snell_shift_task,
    "heat_steps": generate_random_heat_steps_task,
    "hydraulic_lift": generate_random_hydraulic_lift_task,
    "euler_drift": generate_random_euler_drift_task,
    "verlet_push": generate_random_verlet_push_task,
    "drag_coast": generate_random_drag_coast_task,
    "spring_pair": generate_random_spring_pair_task,
    "swing_map": generate_random_swing_map_task,
    "poisson_row": generate_random_poisson_row_task,
    "hydro_line": generate_random_hydro_line_task,
    "force_work": generate_random_force_work_task,
    "rocket_burn": generate_random_rocket_burn_task,
    "projectile_tick": generate_random_projectile_tick_task,
    "lc_tick": generate_random_lc_tick_task,
    "polar_stack": generate_random_polar_stack_task,
    "upwind_row": generate_random_upwind_row_task,
    "branch_decay": generate_random_branch_decay_task,
    "ising_pass": generate_random_ising_pass_task,
    "flow_mix": generate_random_flow_mix_task,
    "box_scope": generate_random_box_scope_task,
    "spike_cut": generate_random_spike_cut_task,
    "twin_box": generate_random_twin_box_task,
    "peak_hold": generate_random_peak_hold_task,
    "crack_close": generate_random_crack_close_task,
    "source_dist": generate_random_source_dist_task,
    "slope_field": generate_random_slope_field_task,
    "charge_run": generate_random_charge_run_task,
    "heun_cool": generate_random_heun_cool_task,
    "log_growth": generate_random_log_growth_task,
    "energy_drift": generate_random_energy_drift_task,
    "pid_track": generate_random_pid_track_task,
    "drive_osc": generate_random_drive_osc_task,
    "two_tank": generate_random_two_tank_task,
    "dose_decay": generate_random_dose_decay_task,
    "wrap_ring": generate_random_wrap_ring_task,
    "age_flow": generate_random_age_flow_task,
    "rotor_drop": generate_random_rotor_drop_task,
    "box_jump": generate_random_box_jump_task,
    "ho_jump": generate_random_ho_jump_task,
    "rovib_line": generate_random_rovib_line_task,
    "zeeman_line": generate_random_zeeman_line_task,
    "qnum_ok": generate_random_qnum_ok_task,
    "shell_fill": generate_random_shell_fill_task,
    "level_deg": generate_random_level_deg_task,
    "path_amp": generate_random_path_amp_task,
    "franck_hertz": generate_random_franck_hertz_task,
    "bond_order": generate_random_bond_order_task,
    "shoot_psi": generate_random_shoot_psi_task,
    "expect_h": generate_random_expect_h_task,
    "sch_defect": generate_random_sch_defect_task,
    "split_energy": generate_random_split_energy_task,
    "tdse_step": generate_random_tdse_step_task,
    "prob_flow": generate_random_prob_flow_task,
    "trial_gap": generate_random_trial_gap_task,
    "qwalk_line": generate_random_qwalk_line_task,
    "mz_port": generate_random_mz_port_task,
    "bound_sign": generate_random_bound_sign_task,
    "ladder_down": generate_random_ladder_down_task,
    "ground_iter": generate_random_ground_iter_task,
    "spin_add": generate_random_spin_add_task,
    "reduce_rho": generate_random_reduce_rho_task,
    "barrier_amp": generate_random_barrier_amp_task,
    "perturb_sum": generate_random_perturb_sum_task,
    "yee_line": generate_random_yee_line_task,
    "shock_jump": generate_random_shock_jump_task,
    "gas_path": generate_random_gas_path_task,
    "pipe_flow": generate_random_pipe_flow_task,
    "stiff_cool": generate_random_stiff_cool_task,
    "heat_back": generate_random_heat_back_task,
    "adiab_row": generate_random_adiab_row_task,
    "com_frac": generate_random_com_frac_task,
    "axis_add": generate_random_axis_add_task,
    "stick_line": generate_random_stick_line_task,
    "cap_spark": generate_random_cap_spark_task,
    "line_force": generate_random_line_force_task,
    "kepler_row": generate_random_kepler_row_task,
    "path_green": generate_random_path_green_task,
    "burst_split": generate_random_burst_split_task,
    "knock_line": generate_random_knock_line_task,
    "first_heat": generate_random_first_heat_task,
    "focus_row": generate_random_focus_row_task,
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
