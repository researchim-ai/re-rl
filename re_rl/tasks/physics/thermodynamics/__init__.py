# re_rl/tasks/physics/thermodynamics/__init__.py

"""Задачи по термодинамике."""

from re_rl.tasks.physics.thermodynamics.gas_laws_task import GasLawsTask
from re_rl.tasks.physics.thermodynamics.heat_transfer_task import HeatTransferTask

__all__ = [
    "GasLawsTask",
    "HeatTransferTask",
]
