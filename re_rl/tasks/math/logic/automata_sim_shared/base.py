"""Симуляция автоматов и клеточных систем.

- DFASimulationTask: принимает ли ДКА заданную строку;
- TuringMachineTask: число единиц на ленте после N шагов машины Тьюринга;
- GameOfLifeTask: состояние поля «Жизни» после k шагов;
- ElementaryCATask: строка одномерного клеточного автомата после k шагов.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _SimBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task












