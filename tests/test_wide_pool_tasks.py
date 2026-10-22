"""Пул: течение, тени, шестерни, монеты, биты, пути, масштаб, нечётные, зеркало, возраст."""

import math
import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.discrete.frobenius_coin.task import coin_pair
from re_rl.tasks.math.geometry.manhattan_paths.task import binom
from re_rl.tasks.registry import registry

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

POOL = [
    "boat_current",
    "shadow_height",
    "gear_ratio",
    "frobenius_coin",
    "bit_count",
    "manhattan_paths",
    "map_scale",
    "odd_sum",
    "mirror_glance",
    "age_gap",
]


def _tasks(task_type, language, difficulty, samples=3):
    for subtype in registry[task_type].TASK_TYPES:
        for seed in range(samples):
            random.seed(seed + difficulty * 5)
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
        assert task.final_answer
        assert "{" not in blob
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)
        if language == "en":
            assert not CYRILLIC.search(blob)
        else:
            assert CYRILLIC.search(task.description)


@pytest.mark.parametrize("task_type", POOL)
def test_wrong_answer_rejected(task_type):
    random.seed(2)
    task = ALL_TASK_GENERATORS[task_type](language="en", difficulty=3)
    assert task.verify("<answer>-987654</answer>") == 0.0


def test_relations():
    random.seed(8)
    boat = ALL_TASK_GENERATORS["boat_current"](task_type="current", difficulty=6)
    assert boat.down == boat.vb + boat.vc
    assert boat.up == boat.vb - boat.vc
    assert boat.vb == (boat.down + boat.up) // 2

    shadow = ALL_TASK_GENERATORS["shadow_height"](task_type="pole", difficulty=4)
    assert shadow.pole * shadow.stick_shadow == shadow.stick * shadow.pole_shadow

    gear = ALL_TASK_GENERATORS["gear_ratio"](task_type="teeth", difficulty=7)
    assert gear.n1 * gear.w1 == gear.n2 * gear.w2

    coins = ALL_TASK_GENERATORS["frobenius_coin"](task_type="largest", difficulty=5)
    assert math.gcd(coins.a, coins.b) == 1
    assert coins.largest == coins.a * coins.b - coins.a - coins.b
    assert coin_pair(coins.largest, coins.a, coins.b) is None
    possible = ALL_TASK_GENERATORS["frobenius_coin"](task_type="possible", difficulty=5)
    assert possible.possible is (coin_pair(possible.amount, possible.a, possible.b) is not None)

    bits = ALL_TASK_GENERATORS["bit_count"](task_type="ones", difficulty=9)
    assert bits.ones == bin(bits.n).count("1")
    assert bits.width == bits.n.bit_length()

    grid = ALL_TASK_GENERATORS["manhattan_paths"](task_type="paths", difficulty=8)
    assert grid.distance == grid.x + grid.y
    assert grid.paths == binom(grid.distance, grid.x)

    scale = ALL_TASK_GENERATORS["map_scale"](task_type="real", difficulty=3)
    assert scale.cm * scale.scale == scale.real * 100

    odds = ALL_TASK_GENERATORS["odd_sum"](task_type="count", difficulty=10)
    assert odds.square == odds.n * odds.n

    mirror = ALL_TASK_GENERATORS["mirror_glance"](task_type="deviation", difficulty=10)
    assert 1 <= mirror.angle <= 85
    assert mirror.glance == 90 - mirror.angle
    assert mirror.deviation == 180 - 2 * mirror.angle
    assert mirror.glance > 0 and mirror.deviation > 0

    ages = ALL_TASK_GENERATORS["age_gap"](task_type="twice", difficulty=6)
    assert ages.older + ages.years == 2 * (ages.young + ages.years)
    assert ages.gap == ages.older - ages.young
