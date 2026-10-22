"""Целочисленный пул: Гук, плотность, средняя скорость, рычаг, работа, смеси, отношение, часы."""

import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

POOL = [
    "hooke_law",
    "density",
    "average_speed",
    "lever_balance",
    "work_rates",
    "mixture_concentration",
    "ratio_split",
    "clock_hands",
]


def _tasks(task_type, language, difficulty, samples=4):
    cls_types = registry[task_type].TASK_TYPES
    for subtype in cls_types:
        for seed in range(samples):
            random.seed(seed + difficulty)
            task = ALL_TASK_GENERATORS[task_type](
                task_type=subtype, language=language, difficulty=difficulty,
            )
            yield task


@pytest.mark.parametrize("task_type", POOL)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", POOL)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    for task in _tasks(task_type, language, difficulty):
        assert task.final_answer is not None
        assert task.solution_steps
        assert "{" not in task.description
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)
        if language == "en":
            blob = task.description + "\n" + "\n".join(task.solution_steps)
            assert not CYRILLIC.search(blob)
        else:
            assert CYRILLIC.search(task.description)


@pytest.mark.parametrize("task_type", POOL)
def test_wrong_answer_rejected(task_type):
    random.seed(1)
    task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=4)
    assert task.verify("<answer>-987654</answer>") == 0.0


def test_integer_relations_hold():
    random.seed(3)
    hooke = ALL_TASK_GENERATORS["hooke_law"](task_type="force", difficulty=6)
    assert hooke.force == hooke.k * hooke.x

    density = ALL_TASK_GENERATORS["density"](task_type="mass", difficulty=7)
    assert density.mass == density.density * density.volume

    speed = ALL_TASK_GENERATORS["average_speed"](task_type="other_speed", difficulty=8)
    assert 2 * speed.v1 * speed.v2 == speed.average * (speed.v1 + speed.v2)

    lever = ALL_TASK_GENERATORS["lever_balance"](task_type="distance", difficulty=5)
    assert lever.m1 * lever.d1 == lever.m2 * lever.d2

    work = ALL_TASK_GENERATORS["work_rates"](task_type="partner", difficulty=9)
    assert work.a * work.b == work.together * (work.a + work.b)

    mix = ALL_TASK_GENERATORS["mixture_concentration"](task_type="second", difficulty=6)
    assert mix.c1 * mix.v1 + mix.c2 * mix.v2 == mix.result * (mix.v1 + mix.v2)
    assert 0 <= mix.result <= 100
    assert 0 <= mix.c2 <= 100

    ratio = ALL_TASK_GENERATORS["ratio_split"](task_type="second", difficulty=4)
    assert ratio.first + ratio.second == ratio.total
    assert ratio.first * ratio.b == ratio.second * ratio.a

    found = False
    for seed in range(80):
        random.seed(seed)
        clock = ALL_TASK_GENERATORS["clock_hands"](task_type="smaller", difficulty=1)
        assert clock.minute == 0
        assert clock.smaller + clock.larger == 360
        assert 0 <= clock.smaller <= 180
        if clock.hour == 3:
            assert clock.answer == 90
            found = True
            break
    assert found
