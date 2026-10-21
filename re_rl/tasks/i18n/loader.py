"""Загрузка двуязычных текстов задач из JSON."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_I18N_DIR = Path(__file__).resolve().parent
_TASKS_ROOT = _I18N_DIR.parent


def clear_cache() -> None:
    """Сбрасывает кэш JSON. Нужен тестам, которые подменяют файлы."""
    _read_json.cache_clear()


@lru_cache(maxsize=None)
def _read_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dig(node: Any, key: str) -> Any:
    cur = node
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(key)
        cur = cur[part]
    return cur


def _render(node: Any, language: str, augment: bool, kwargs: Dict[str, Any], key: str) -> str:
    if isinstance(node, str):
        template = node
    elif isinstance(node, dict) and ("ru" in node or "en" in node):
        value = node.get(language, node.get("en", ""))
        if isinstance(value, list):
            if not value:
                return ""
            template = random.choice(value) if augment else value[0]
        elif isinstance(value, str):
            template = value
        else:
            raise KeyError(key)
    else:
        raise KeyError(key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def _lookup(data: Dict[str, Any], key: str) -> Any:
    """Ищет ключ в text, inline_keys и prompt — в таком порядке."""
    if not key:
        raise KeyError(key)
    roots = []
    for name in ("text", "inline_keys", "prompt"):
        node = data.get(name)
        if isinstance(node, dict):
            roots.append(node)
    roots.append(data)
    for root in roots:
        cur: Any = root
        ok = True
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok:
            return cur
    raise KeyError(key)


class TaskTexts:
    """Тексты одного модуля: соседний JSON и общий каталог."""

    def __init__(self, anchor: str, filename: str = "i18n.json"):
        path = Path(anchor)
        if path.suffix == ".json":
            self.path = path
        elif path.suffix == ".py":
            self.path = path.resolve().with_name(filename)
        else:
            self.path = path / filename

    def _data(self) -> Dict[str, Any]:
        if not self.path.is_file():
            return {}
        data = _read_json(str(self.path))
        if not isinstance(data, dict):
            raise TypeError(f"Expected a JSON object in {self.path}")
        return data

    def t(self, key: str, language: str, augment: bool = True, **kwargs: Any) -> str:
        """Возвращает строку задачи. Неизвестный ключ — KeyError."""
        try:
            node = _lookup(self._data(), key)
        except KeyError as exc:
            raise KeyError(f"{key} ({self.path})") from exc
        return _render(node, language, augment, kwargs, key)

    def raw(self, key: Optional[str] = None) -> Any:
        """Возвращает узел каталога без форматирования."""
        data = self._data()
        if key is None:
            prompt = data.get("prompt")
            return prompt if prompt is not None else data
        try:
            return _lookup(data, key)
        except KeyError as exc:
            raise KeyError(f"{key} ({self.path})") from exc

    def literal(self, key: str) -> str:
        """Строка, не зависящая от языка (формула, регулярное выражение)."""
        node = self.raw(key)
        if not isinstance(node, str):
            raise TypeError(f"{key} is not a string")
        return node

    def common(self, key: str, language: str, augment: bool = True, **kwargs: Any) -> str:
        return common_text(key, language, augment=augment, **kwargs)

    def common_node(self, key: str) -> Any:
        return common_node(key)


def common_path() -> Path:
    return _I18N_DIR / "common.json"


def common_node(key: str) -> Any:
    data = _read_json(str(common_path()))
    try:
        return _dig(data, key)
    except KeyError as exc:
        raise KeyError(f"{key} (common)") from exc


def common_text(key: str, language: str, augment: bool = True, **kwargs: Any) -> str:
    return _render(common_node(key), language, augment, kwargs, key)


def load_system_prompts() -> Dict[str, Any]:
    return common_node("system")


def get_random_system_prompt(language: str = "ru", style: Optional[str] = None) -> str:
    """Возвращает системный промпт. Без style выбирается случайный вариант."""
    prompts = load_system_prompts()
    bucket = prompts.get(language, prompts.get("en", {}))
    if style and style in bucket:
        return bucket[style]
    return random.choice(list(bucket.values()))


def get_template(
    templates: Dict[str, Any],
    key: str,
    language: str,
    augment: bool = True,
    **kwargs: Any,
) -> str:
    """Совместимый доступ к словарю шаблонов: язык, список вариантов, format."""
    template_data = templates.get(key, {})
    if not isinstance(template_data, dict):
        value = ""
    else:
        value = template_data.get(language, template_data.get("en", ""))
    if isinstance(value, list):
        if not value:
            return ""
        template = random.choice(value) if augment else value[0]
    else:
        template = value
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def _load_fragment(spec: str) -> Any:
    path, _, frag = spec.partition("#")
    data = _read_json(str(_TASKS_ROOT / path))
    if not frag:
        return data
    node = data
    for part in frag.split("."):
        node = node[part]
    return node


def load_prompt_templates() -> Dict[str, Any]:
    """Собирает прежний PROMPT_TEMPLATES из общего JSON и каталогов задач."""
    common = _read_json(str(common_path()))
    templates: Dict[str, Any] = {
        "default": common["default"],
        "inline": dict(common.get("inline", {})),
        "multiturn": common["multiturn"],
    }
    index_path = _I18N_DIR / "sections.json"
    if index_path.is_file():
        index = _read_json(str(index_path))
        for section, spec in index.items():
            templates[section] = _load_fragment(spec)
    inline_index_path = _I18N_DIR / "inline_index.json"
    if inline_index_path.is_file():
        inline_index = _read_json(str(inline_index_path))
        for key, spec in inline_index.items():
            templates["inline"][key] = _load_fragment(spec)
    return templates


def iter_locale_leaves(node: Any, path: str = ""):
    """Листья с парой ru/en. Обычные строки и вложенные словари языка не листья."""
    if isinstance(node, dict):
        ru = node.get("ru") if "ru" in node else None
        en = node.get("en") if "en" in node else None
        localized = ("ru" in node or "en" in node) and (
            isinstance(ru, (str, list)) or isinstance(en, (str, list)) or ru is None or en is None
        )
        if localized and not isinstance(ru, dict) and not isinstance(en, dict):
            yield path, node
            return
        for key, value in node.items():
            if str(key).startswith("$"):
                continue
            child = f"{path}.{key}" if path else str(key)
            yield from iter_locale_leaves(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from iter_locale_leaves(value, f"{path}[{index}]")
