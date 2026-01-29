# re_rl/tasks/physics/waves/__init__.py

"""Задачи по волнам и оптике."""

from re_rl.tasks.physics.waves.waves_task import WavesTask
from re_rl.tasks.physics.waves.optics_task import OpticsTask
from re_rl.tasks.physics.waves.doppler_effect_task import DopplerEffectTask
from re_rl.tasks.physics.waves.interference_task import InterferenceTask
from re_rl.tasks.physics.waves.diffraction_task import DiffractionTask
from re_rl.tasks.physics.waves.polarization_task import PolarizationTask

__all__ = [
    "WavesTask",
    "OpticsTask",
    "DopplerEffectTask",
    "InterferenceTask",
    "DiffractionTask",
    "PolarizationTask",
]
