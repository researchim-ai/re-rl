from __future__ import annotations
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'registry_i18n.json')


texts.literal('literals.s0')

from typing import Dict, Type

registry: Dict[str, Type["BaseTask"]] = {}

__all__ = ["registry"] 
