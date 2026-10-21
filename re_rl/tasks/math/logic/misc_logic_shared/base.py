"""Разные логические задачи: расшифровка шифра (Цезарь / подстановка), принцип
Дирихле, парадокс Монти Холла и отношения Аллена между интервалами."""

import random
import string
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _MiscBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


def _letters_only(s: str) -> str:
    return "".join(ch for ch in s.lower() if "a" <= ch <= "z")












