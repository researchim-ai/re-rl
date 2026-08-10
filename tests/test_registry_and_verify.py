"""Тесты инфраструктуры: синхронизация реестра, README и хук verify()."""

import re
from pathlib import Path

import pytest

from re_rl.tasks.registry import registry
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


def test_all_generators_are_registered():
    """Каждый тип из ALL_TASK_GENERATORS должен присутствовать в реестре."""
    missing = [t for t in ALL_TASK_GENERATORS if t not in registry]
    assert not missing, f"Типы есть в генераторах, но не в registry: {missing}"


def test_readme_task_count_matches_registry():
    """Число типов в README должно совпадать с фактическим (защита от рассинхрона)."""
    readme = Path(__file__).resolve().parents[1] / "README.md"
    text = readme.read_text(encoding="utf-8")
    match = re.search(r"\*\*(\d+)\s+тип\w*\s+задач\*\*", text)
    assert match, "В README не найдена строка с количеством типов задач"
    declared = int(match.group(1))
    assert declared == len(ALL_TASK_GENERATORS), (
        f"README заявляет {declared} типов, но ALL_TASK_GENERATORS содержит "
        f"{len(ALL_TASK_GENERATORS)}. Обновите README."
    )


def test_physics_count_split():
    total = len(ALL_TASK_GENERATORS)
    physics = len(ALL_PHYSICS_TASK_GENERATORS)
    assert physics > 0
    assert total - physics > 0


def test_base_verify_hook_numeric():
    """verify() по умолчанию должен корректно оценивать числовой ответ.

    Заодно проверяет числовой fallback в compare_answers: у arithmetic нет
    специального компаратора, но ответ всё равно сравнивается численно.
    """
    task = ALL_TASK_GENERATORS["arithmetic"](language="ru", difficulty=2)
    task.get_result()  # гарантируем solve()
    ref = str(task.final_answer)
    assert task.verify(f"<answer>{ref}</answer>") == pytest.approx(1.0)
    assert task.verify("<answer>999999999</answer>") == pytest.approx(0.0)
