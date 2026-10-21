"""Фасад: прежние шаблоны собираются из JSON каталогов задач."""

from re_rl.tasks.i18n import (
    get_random_system_prompt,
    get_template,
    load_prompt_templates,
    load_system_prompts,
)

__all__ = [
    "PROMPT_TEMPLATES",
    "SYSTEM_PROMPT_VARIATIONS",
    "get_template",
    "get_random_system_prompt",
]


def __getattr__(name):
    if name == "PROMPT_TEMPLATES":
        return load_prompt_templates()
    if name == "SYSTEM_PROMPT_VARIATIONS":
        return load_system_prompts()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
