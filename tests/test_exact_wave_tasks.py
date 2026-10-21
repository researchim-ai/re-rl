"""Точные задачи волны: Лагранж, Эйлер, дробный рюкзак, СНМ, кэш, конь,
адиабата и баллистический маятник.

Проверяются регистрация, самосогласованность, отказ от неверного ответа
и ручные эталоны алгоритмов.
"""

import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.analysis.lagrange_task import lagrange_at, _eval_poly
from re_rl.tasks.math.analysis.euler_method_task import euler_trace
from re_rl.tasks.math.logic.fractional_knapsack_task import fractional_value
from re_rl.tasks.math.discrete.union_find_task import _DSU
from re_rl.tasks.math.logic.cache_task import simulate, locate
from re_rl.tasks.math.logic.knight_moves_task import knight_path, parse_square
from re_rl.tasks.physics.thermodynamics.adiabatic_task import AdiabaticTask
from re_rl.tasks.physics.mechanics.ballistic_pendulum_task import BallisticPendulumTask

EXACT_TYPES = [
    "lagrange_interpolation", "euler_method", "fractional_knapsack", "union_find",
    "direct_mapped_cache", "knight_moves", "adiabatic", "ballistic_pendulum",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


@pytest.mark.parametrize("task_type", EXACT_TYPES)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", EXACT_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(3):
            _seed(task_type, sub, language, difficulty, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language=language, difficulty=difficulty, **kwargs)
            assert task.final_answer is not None
            assert "{" not in task.description and "}" not in task.description
            assert task.solution_steps
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", EXACT_TYPES)
@pytest.mark.parametrize("difficulty", [2, 8])
def test_wrong_answer_rejected(task_type, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(3):
            _seed("wrong", task_type, sub, difficulty, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language="ru", difficulty=difficulty, **kwargs)
            fa = str(task.final_answer).strip()
            low = fa.lower()
            if low in ("да", "yes", "истина"):
                wrong = "нет"
            elif low in ("нет", "no", "ложь"):
                wrong = "да"
            elif re.fullmatch(r"-?\d+", fa):
                wrong = str(int(fa) + 7)
            else:
                wrong = "zzqqx"
            assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_lagrange_matches_polynomial():
    xs, ys = [0, 1], [1, 3]  # 2x + 1
    assert lagrange_at(xs, ys, 2) == 5
    assert lagrange_at(xs, ys, 4) == _eval_poly([1, 2], 4)


def test_euler_known():
    # y' = y, y(0) = 1, три шага: 2, 4, 8
    trace = euler_trace(0, 1, 0, 1, 0, 3)
    assert [y for _, y in trace] == [1, 2, 4, 8]


def test_fractional_knapsack_known():
    # плотности 3 и 2, вместимость 3: весь первый (6) и 1 единица второго (2)
    total, taken = fractional_value([(2, 6), (3, 6)], 3)
    assert total == 8
    assert taken[0][2] == 0 and taken[0][0] == 2
    assert taken[1][0] == 1 and taken[1][1] == 2


def test_union_find_known():
    dsu = _DSU(4)
    assert dsu.union(1, 2) and dsu.union(2, 3)
    assert dsu.union(1, 3) is False
    assert dsu.components(4) == 2
    assert dsu.find(1) == dsu.find(3)
    assert dsu.find(1) != dsu.find(4)
    assert dsu.size[dsu.find(1)] == 3


def test_cache_known():
    # блок 4, 4 строки. 0 miss, 4 miss, 0 hit, 16 вытесняет 0, затем 0 снова miss
    hits, misses, _ = simulate([0, 4, 0, 16, 0], 4, 4)
    assert hits == 1 and misses == 4
    assert locate(16, 4, 4) == (1, 0)


def test_knight_known():
    assert len(knight_path(parse_square("a1"), parse_square("b3"))) - 1 == 1
    assert len(knight_path(parse_square("a1"), parse_square("c2"))) - 1 == 1
    assert len(knight_path(parse_square("a1"), parse_square("a1"))) - 1 == 0
    assert len(knight_path(parse_square("a1"), parse_square("h8"))) - 1 == 6


def test_adiabatic_identities():
    _seed("adia", 1)
    for sub in AdiabaticTask.TASK_TYPES:
        task = AdiabaticTask.generate_random_task(task_type=sub, difficulty=9)
        task._check()
        assert task.verify(f"<answer>{task.answer}</answer>") == 1.0


def test_ballistic_identities():
    _seed("ball", 2)
    for sub in BallisticPendulumTask.TASK_TYPES:
        task = BallisticPendulumTask.generate_random_task(task_type=sub, difficulty=8)
        assert task.m * task.v == task.V * (task.m + task.M)
        assert task.V * task.V == 20 * task.h
        assert task.answer == {"block_speed": task.V, "height": task.h, "bullet_speed": task.v}[sub]
