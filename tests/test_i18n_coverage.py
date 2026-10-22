"""Каталоги переводов полны, английская генерация не содержит кириллицы."""

import json
import random
import re
from pathlib import Path

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.i18n.loader import iter_locale_leaves

CYRILLIC = re.compile(r"[А-Яа-яЁё]")
ROOT = Path(__file__).resolve().parents[1] / "re_rl"


def test_every_locale_leaf_has_both_languages():
    incomplete = []
    for path in ROOT.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for leaf_path, node in iter_locale_leaves(data):
            if "ru" not in node or "en" not in node:
                incomplete.append(f"{path.relative_to(ROOT)}:{leaf_path}")
            elif isinstance(node["ru"], list) or isinstance(node["en"], list):
                if not isinstance(node["ru"], list) or not isinstance(node["en"], list):
                    incomplete.append(f"{path.relative_to(ROOT)}:{leaf_path}")
    assert incomplete == []


@pytest.mark.parametrize("language", ["ru", "en"])
def test_generated_text_matches_language(language):
    leaks = []
    empty = []
    for name, generate in sorted(ALL_TASK_GENERATORS.items()):
        random.seed(1)
        try:
            try:
                task = generate(language=language, detail_level=2, difficulty=2)
            except TypeError:
                task = generate(language=language)
            if task.final_answer is None:
                task.solve()
        except Exception as exc:  # noqa: BLE001 — генератор сообщает о себе в списке
            leaks.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        blob = (task.description or "") + "\n" + "\n".join(map(str, task.solution_steps or []))
        if not blob.strip():
            empty.append(name)
        if language == "en" and CYRILLIC.search(blob):
            leaks.append(name)
        if language == "ru" and not blob.strip():
            empty.append(name)
    assert leaks == []
    assert empty == []


def test_english_catalog_has_no_cyrillic():
    leaked = []
    for path in ROOT.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for leaf_path, node in iter_locale_leaves(data):
            en = node.get("en")
            chunks = en if isinstance(en, list) else [en]
            for chunk in chunks:
                if isinstance(chunk, str) and CYRILLIC.search(chunk) and "А-Я" not in chunk:
                    leaked.append(f"{path.relative_to(ROOT)}:{leaf_path}")
    assert leaked == []


def test_edge_difficulties_and_sequence_wording():
    from re_rl.tasks.math.discrete.sequence.task import SequenceTask
    from re_rl.tasks.physics.quantum.quantum.task import QuantumTask
    from re_rl.tasks.physics.thermodynamics.gas_laws.task import GasLawsTask

    for cls in (SequenceTask, GasLawsTask, QuantumTask):
        for task_type in cls.TASK_TYPES:
            for language in ("ru", "en"):
                for difficulty in (1, 10):
                    random.seed(1)
                    task = cls.generate_random_task(
                        task_type=task_type, language=language, difficulty=difficulty,
                    )
                    if task.final_answer is None:
                        task.solve()
                    blob = (task.description or "") + "\n" + "\n".join(map(str, task.solution_steps or []))
                    assert blob.strip(), f"{cls.__name__}/{task_type}/{language}"
                    if language == "en":
                        assert not CYRILLIC.search(blob), f"{cls.__name__}/{task_type}"

    task = SequenceTask(task_type="recurrence", language="ru", difficulty=10)
    assert "a_{n}" in task.description

    saw_primes = False
    for seed in range(80):
        random.seed(seed)
        task = SequenceTask(task_type="pattern", language="en", difficulty=2)
        task.solve()
        if task.pattern_name != "primes":
            continue
        saw_primes = True
        blob = "\n".join(map(str, task.solution_steps))
        assert "prime numbers" in blob
        assert not CYRILLIC.search(blob)
        break
    assert saw_primes
