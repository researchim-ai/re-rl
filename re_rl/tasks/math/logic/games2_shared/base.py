"""Игры с оптимальной стратегией: набор комбинаторных игр (мизерный Ним, игра
Витоффа, ход в игре вычитания, Chomp) и крестики-нолики (минимакс)."""

import math
import random
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_PHI = (1 + 5 ** 0.5) / 2


class _GameBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task






