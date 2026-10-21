"""Тесты загрузчика переводов."""

import json

import pytest

from re_rl.tasks.i18n.loader import TaskTexts, clear_cache, get_template, iter_locale_leaves


@pytest.fixture(autouse=True)
def _clear():
    clear_cache()
    yield
    clear_cache()


def test_language_fallback_and_format(tmp_path):
    path = tmp_path / "i18n.json"
    path.write_text(
        json.dumps(
            {
                "text": {
                    "greet": {
                        "en": "Hello, {name}",
                        "ru": "Привет, {name}",
                    }
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    texts = TaskTexts(path)
    assert texts.t("greet", "ru", name="Анна") == "Привет, Анна"
    assert texts.t("greet", "de", name="Ann") == "Hello, Ann"


def test_augment_list_is_stable_when_disabled(tmp_path):
    path = tmp_path / "i18n.json"
    path.write_text(
        json.dumps({"text": {"q": {"ru": ["первый", "второй"], "en": ["first", "second"]}}}),
        encoding="utf-8",
    )
    texts = TaskTexts(path)
    assert texts.t("q", "ru", augment=False) == "первый"
    assert texts.t("q", "en", augment=False) == "first"


def test_missing_key_raises(tmp_path):
    path = tmp_path / "i18n.json"
    path.write_text("{}", encoding="utf-8")
    texts = TaskTexts(path)
    with pytest.raises(KeyError):
        texts.t("absent", "ru")


def test_dotted_prompt_and_formula(tmp_path):
    path = tmp_path / "i18n.json"
    path.write_text(
        json.dumps(
            {
                "prompt": {"problem": {"uniform": {"ru": "путь {s}", "en": "path {s}"}}},
                "text": {"formula": "s = vt"},
            }
        ),
        encoding="utf-8",
    )
    texts = TaskTexts(path)
    assert texts.t("problem.uniform", "en", s=3) == "path 3"
    assert texts.literal("formula") == "s = vt"
    assert texts.raw("problem")["uniform"]["ru"] == "путь {s}"


def test_get_template_matches_historical_rules():
    templates = {"problem": {"ru": ["A {x}", "B {x}"], "en": "C {x}"}}
    assert get_template(templates, "problem", "ru", augment=False, x=1) == "A 1"
    assert get_template(templates, "problem", "fr", augment=False, x=1) == "C 1"
    assert get_template(templates, "missing", "ru") == ""
    assert get_template(templates, "problem", "en", augment=False, y=1) == "C {x}"


def test_locale_leaf_walker_requires_pairs():
    catalog = {
        "prompt": {"step": {"ru": "шаг", "en": "step"}, "formula": "E = mc^2"},
        "text": {"only_ru": {"ru": "да"}},
    }
    leaves = dict(iter_locale_leaves(catalog))
    assert leaves["prompt.step"]["en"] == "step"
    assert "prompt.formula" not in leaves
    assert "text.only_ru" in leaves
    incomplete = [path for path, node in leaves.items() if "ru" not in node or "en" not in node]
    assert incomplete == ["text.only_ru"]
