from __future__ import annotations

"""Central registry of all Task subclasses.
Every concrete Task class is automatically added using the metaclass in
`BaseTask`.  The mapping key is so-called *task type* – короткая строка
(например, "linear", "quadratic"), которая используется генераторами
задач и окружениями RL.

External code should import `registry` and use:
    cls = registry[task_type]

Используйте `get` для безопасного доступа или ловите KeyError.
"""

from typing import Dict, Type

registry: Dict[str, Type["BaseTask"]] = {}

__all__ = ["registry"] 