"""Разнородный пул: углы, эхо, делители, диагональ сетки, цифровой корень, кубики, треугольник, Джоуль."""

import math
import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.discrete.digital_root.task import digit_chain
from re_rl.tasks.math.discrete.divisor_sum.task import positive_divisors
from re_rl.tasks.math.geometry.triangle_sides.task import is_triangle
from re_rl.tasks.math.probability.dice_ways.task import ways_for_sum
from re_rl.tasks.registry import registry

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

POOL = [
    "polygon_angles",
    "echo_delay",
    "divisor_sum",
    "grid_diagonal",
    "digital_root",
    "dice_ways",
    "triangle_sides",
    "joule_heat",
]


def _tasks(task_type, language, difficulty, samples=4):
    for subtype in registry[task_type].TASK_TYPES:
        for seed in range(samples):
            random.seed(seed + difficulty * 3)
            yield ALL_TASK_GENERATORS[task_type](
                task_type=subtype, language=language, difficulty=difficulty,
            )


@pytest.mark.parametrize("task_type", POOL)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", POOL)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    for task in _tasks(task_type, language, difficulty):
        blob = task.description + "\n" + "\n".join(task.solution_steps)
        assert task.final_answer is not None
        assert task.solution_steps
        assert "{" not in blob
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)
        if language == "en":
            assert not CYRILLIC.search(blob)
        else:
            assert CYRILLIC.search(task.description)


@pytest.mark.parametrize("task_type", POOL)
def test_wrong_answer_rejected(task_type):
    random.seed(1)
    task = ALL_TASK_GENERATORS[task_type](language="en", difficulty=4)
    assert task.verify("<answer>-987654</answer>") == 0.0


def test_relations():
    random.seed(5)
    polygon = ALL_TASK_GENERATORS["polygon_angles"](task_type="angle", difficulty=8)
    assert polygon.sum == (polygon.n - 2) * 180
    assert polygon.sum % polygon.n == 0
    assert polygon.diagonals == polygon.n * (polygon.n - 3) // 2

    echo = ALL_TASK_GENERATORS["echo_delay"](task_type="time", difficulty=6)
    assert echo.distance * 2 == 340 * echo.time

    divisors = ALL_TASK_GENERATORS["divisor_sum"](task_type="total", difficulty=9)
    found = positive_divisors(divisors.n)
    assert found == divisors.divisors
    assert divisors.total == sum(found)

    grid = ALL_TASK_GENERATORS["grid_diagonal"](task_type="interior", difficulty=7)
    assert grid.squares == grid.m + grid.n - math.gcd(grid.m, grid.n)
    assert grid.interior == math.gcd(grid.m, grid.n) - 1

    root = ALL_TASK_GENERATORS["digital_root"](task_type="steps", difficulty=10)
    chain, value, steps = digit_chain(root.n)
    assert (value, steps) == (root.root, root.steps)
    assert value == 1 + (root.n - 1) % 9
    assert chain == root.chain

    dice = ALL_TASK_GENERATORS["dice_ways"](task_type="ways", difficulty=3)
    assert dice.ways == ways_for_sum(dice.faces, dice.total)

    smaller = ALL_TASK_GENERATORS["dice_ways"](task_type="smaller_sum", difficulty=4)
    assert ways_for_sum(smaller.faces, smaller.answer) == smaller.ways
    other = 2 * smaller.faces + 1 - smaller.ways
    assert smaller.answer <= other

    sides = ALL_TASK_GENERATORS["triangle_sides"](task_type="possible", difficulty=2)
    assert sides.possible is is_triangle(sides.a, sides.b, sides.c)
    longest = ALL_TASK_GENERATORS["triangle_sides"](task_type="max_side", difficulty=2)
    assert longest.answer == longest.a + longest.b - 1
    assert is_triangle(longest.a, longest.b, longest.answer)
    assert not is_triangle(longest.a, longest.b, longest.answer + 1)

    heat = ALL_TASK_GENERATORS["joule_heat"](task_type="current", difficulty=8)
    assert heat.heat == heat.i * heat.i * heat.r * heat.t
