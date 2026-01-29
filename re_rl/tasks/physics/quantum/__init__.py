# re_rl/tasks/physics/quantum/__init__.py

"""Задачи по квантовой механике."""

from re_rl.tasks.physics.quantum.quantum_task import QuantumTask
from re_rl.tasks.physics.quantum.bohr_model_task import BohrModelTask
from re_rl.tasks.physics.quantum.de_broglie_task import DeBroglieTask
from re_rl.tasks.physics.quantum.uncertainty_principle_task import UncertaintyPrincipleTask
from re_rl.tasks.physics.quantum.radioactive_decay_task import RadioactiveDecayTask

__all__ = [
    "QuantumTask",
    "BohrModelTask",
    "DeBroglieTask",
    "UncertaintyPrincipleTask",
    "RadioactiveDecayTask",
]
