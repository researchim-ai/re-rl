"""Тесты для новейшей волны физических задач (7 типов).

Проверяем регистрацию, самосогласованность (эталон засчитывается),
отсутствие неподставленных плейсхолдеров и отклонение заведомо неверных ответов
на всех уровнях сложности и обоих языках.
"""

import random

import numpy as np
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


def _seed(s=0):
    random.seed(s)
    np.random.seed(s)


LATEST_PHYSICS_TYPES = [
    "elasticity", "terminal_velocity", "surface_tension",
    "wheatstone_bridge", "gas_work", "mean_free_path", "pair_production",
]


@pytest.mark.parametrize("task_type", LATEST_PHYSICS_TYPES)
def test_registered_globally(task_type):
    assert task_type in ALL_TASK_GENERATORS
    assert task_type in ALL_PHYSICS_TASK_GENERATORS


@pytest.mark.parametrize("task_type", LATEST_PHYSICS_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    _seed(difficulty)
    for _ in range(6):
        task = ALL_PHYSICS_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
        task.solve()
        assert task.final_answer is not None
        assert len(task.solution_steps) >= 1
        assert "{" not in task.description
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


@pytest.mark.parametrize("task_type", LATEST_PHYSICS_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_wrong_answer_rejected(task_type, language, difficulty):
    """Ответ, гарантированно отличающийся от эталона более чем на 2%, отклоняется."""
    _seed(100 + difficulty)
    for _ in range(6):
        task = ALL_PHYSICS_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
        task.solve()
        ref = task._answer_numbers[-1]
        # Значение, заведомо далёкое от эталона (≈ утроенное со сдвигом).
        wrong = ref * 3.0 + 7.77 if ref != 0 else 12345.0
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_elasticity_label_robust():
    """Подпись величины в ответе не мешает извлечь число."""
    _seed(7)
    task = ALL_PHYSICS_TASK_GENERATORS["elasticity"](
        task_type="elongation", language="ru", difficulty=5)
    task.solve()
    dL = task._answer_numbers[-1]
    assert task.verify(f"<answer>удлинение стержня ΔL = {dL:.6e} м</answer>") == pytest.approx(1.0)


def test_pair_production_threshold_value():
    """Порог рождения пары ≈ 1.022 МэВ."""
    _seed(3)
    task = ALL_PHYSICS_TASK_GENERATORS["pair_production"](
        task_type="threshold_energy", language="en", difficulty=5)
    task.solve()
    assert task.verify("<answer>1.022 MeV</answer>") == pytest.approx(1.0)
