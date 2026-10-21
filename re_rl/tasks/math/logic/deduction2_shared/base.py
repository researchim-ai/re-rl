"""Дедуктивные задачи: логическая сетка соответствий, круговая рассадка,
турнирные подсчёты (круговой и на выбывание)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_NAMES = [texts.literal('literals.s0'), texts.literal('literals.s1'), texts.literal('literals.s2'), texts.literal('literals.s3'), texts.literal('literals.s4'), texts.literal('literals.s5')]
_NAMES_EN = ["Anna", "Boris", "Vera", "Gleb", "Dina", "Egor"]
_TEAMS = [texts.literal('literals.s6'), texts.literal('literals.s7'), texts.literal('literals.s8'), texts.literal('literals.s9'), texts.literal('literals.s10'), texts.literal('literals.s11'), texts.literal('literals.s12'), texts.literal('literals.s13')]
_TEAMS_EN = ["Alpha", "Bravo", "Victor", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]


class _DedBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task









