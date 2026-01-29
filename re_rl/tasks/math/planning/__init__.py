# re_rl/tasks/math/planning/__init__.py

"""Задачи на планирование и поиск."""

from re_rl.tasks.math.planning.river_crossing_task import RiverCrossingTask
from re_rl.tasks.math.planning.tower_of_hanoi_task import TowerOfHanoiTask
from re_rl.tasks.math.planning.water_jug_task import WaterJugTask

__all__ = [
    "RiverCrossingTask",
    "TowerOfHanoiTask", 
    "WaterJugTask",
]
