"""Графики движения (визуальные задачи, matplotlib).

- ``KinematicsGraphTask`` — график скорости v(t) (ломаная по целым узлам):
  подтипы ``displacement`` (перемещение = площадь под v–t) и ``acceleration``
  (ускорение на выделенном участке = наклон);
- ``ProjectileGraphTask`` — траектория брошенного тела (парабола):
  подтипы ``range`` (дальность) и ``max_height`` (максимальная высота).

Значения подобраны целыми и читаются по координатной сетке.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U






