"""Тесты для масштабируемых (многошаговых) физических задач (6 типов).

Проверяем регистрацию, самосогласованность, отсутствие неподставленных
плейсхолдеров, отклонение заведомо неверных ответов и рост сложности
(число элементов N увеличивается с уровнем).
"""

import random

import numpy as np
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


def _seed(s=0):
    random.seed(s)
    np.random.seed(s)


SCALABLE_TYPES = [
    "series_parallel_network", "pv_cycle", "elastic_chain",
    "abcd_optics", "composite_inertia", "calorimetry_mix",
]


@pytest.mark.parametrize("task_type", SCALABLE_TYPES)
def test_registered_globally(task_type):
    assert task_type in ALL_TASK_GENERATORS
    assert task_type in ALL_PHYSICS_TASK_GENERATORS


@pytest.mark.parametrize("task_type", SCALABLE_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    _seed(difficulty)
    for _ in range(8):
        task = ALL_PHYSICS_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
        task.solve()
        assert task.final_answer is not None
        assert len(task.solution_steps) >= 1
        assert "{" not in task.description
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


@pytest.mark.parametrize("task_type", SCALABLE_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_wrong_answer_rejected(task_type, language, difficulty):
    """Ответ с большим абсолютным смещением от эталона отклоняется."""
    _seed(200 + difficulty)
    for _ in range(8):
        task = ALL_PHYSICS_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
        task.solve()
        ref = task._answer_numbers[-1]
        wrong = ref + abs(ref) + 50.0 + 0.123  # гарантированно > 2% допуска
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_series_parallel_all_domains():
    """Каждый домен даёт корректный физический эквивалент."""
    _seed(1)
    for domain in ("resistor", "capacitor", "spring", "thermal"):
        task = ALL_PHYSICS_TASK_GENERATORS["series_parallel_network"](
            task_type=domain, difficulty=6)
        task.solve()
        assert task._answer_numbers[0] > 0
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


def test_series_parallel_two_series_resistors():
    """Два резистора последовательно = сумме (проверка движка на простом случае)."""
    _seed(3)
    task = ALL_PHYSICS_TASK_GENERATORS["series_parallel_network"](
        task_type="resistor", difficulty=1)
    # Принудительно зададим простое дерево из двух резисторов.
    task.tree = ("series", ("leaf", 10), ("leaf", 30))
    task.solve()
    assert task._answer_numbers[0] == pytest.approx(40.0)


def test_composite_point_masses_value():
    _seed(5)
    task = ALL_PHYSICS_TASK_GENERATORS["composite_inertia"](
        task_type="point_masses", difficulty=4)
    expected = sum(m * r ** 2 for m, r in task.pairs)
    assert task._answer_numbers[0] == pytest.approx(expected)


def test_difficulty_scales_element_count():
    """С ростом сложности число элементов в сети не убывает."""
    _seed(9)
    low = ALL_PHYSICS_TASK_GENERATORS["series_parallel_network"](
        task_type="resistor", difficulty=1)
    high = ALL_PHYSICS_TASK_GENERATORS["series_parallel_network"](
        task_type="resistor", difficulty=10)
    assert high.n >= low.n
