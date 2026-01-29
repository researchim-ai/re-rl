# re_rl/tasks/physics/thermodynamics/__init__.py

"""Задачи по термодинамике."""

from re_rl.tasks.physics.thermodynamics.gas_laws_task import GasLawsTask
from re_rl.tasks.physics.thermodynamics.heat_transfer_task import HeatTransferTask
from re_rl.tasks.physics.thermodynamics.thermodynamic_cycles_task import ThermodynamicCyclesTask
from re_rl.tasks.physics.thermodynamics.entropy_task import EntropyTask
from re_rl.tasks.physics.thermodynamics.phase_transitions_task import PhaseTransitionsTask

__all__ = [
    "GasLawsTask",
    "HeatTransferTask",
    "ThermodynamicCyclesTask",
    "EntropyTask",
    "PhaseTransitionsTask",
]
