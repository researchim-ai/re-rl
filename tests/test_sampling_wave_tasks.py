"""Волна семплирования и точных формул: V-trace, приоритеты, обрезка наград,
абсолютная ошибка, Жаккар, обратный ранг, подмассивы, целый корень,
произведение, Доплер, Хаббл и свободное падение."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.vtrace_task import vtrace_step
from re_rl.tasks.rl.priority_replay_task import replay_parts
from re_rl.tasks.rl.reward_clip_task import clip_rewards
from re_rl.tasks.rl.discounted_return_task import discounted
from re_rl.tasks.ml.mae_task import absolute_errors
from re_rl.tasks.ml.jaccard_task import jaccard_parts
from re_rl.tasks.ml.reciprocal_rank_task import reciprocal_rank
from re_rl.tasks.math.logic.subarray_sum_task import subarray_count
from re_rl.tasks.math.discrete.integer_sqrt_task import isqrt_pair
from re_rl.tasks.math.logic.max_product_task import max_product
from re_rl.tasks.physics.waves.doppler_shift_task import doppler_observed
from re_rl.tasks.physics.astrophysics.hubble_task import hubble_speed
from re_rl.tasks.physics.mechanics.free_fall_task import fall_height

WAVE = [
    "vtrace", "priority_replay", "reward_clip",
    "mae_loss", "jaccard_index", "reciprocal_rank",
    "subarray_sum", "integer_sqrt", "max_product",
    "doppler_shift", "hubble_law", "free_fall",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


def _brute_product(nums):
    best = nums[0]
    for i in range(len(nums)):
        running = 1
        for j in range(i, len(nums)):
            running *= nums[j]
            if running > best:
                best = running
    return best


def _brute_subarrays(nums, target):
    count = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            count += total == target
    return count


@pytest.mark.parametrize("task_type", WAVE)
def test_registered(task_type):
    assert task_type in registry and task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", WAVE)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(2):
            _seed(task_type, sub, language, difficulty, i)
            task = gen(task_type=sub, language=language, difficulty=difficulty)
            assert "{" not in task.description and "}" not in task.description
            assert task.solution_steps
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", WAVE)
def test_wrong_answer_rejected(task_type):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        _seed("bad", task_type, sub)
        task = gen(task_type=sub, language="ru", difficulty=6)
        if re.fullmatch(r"-?\d+", str(task.final_answer).strip()):
            wrong = str(int(task.final_answer) + 9)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_answers():
    rho, target = vtrace_step(Fraction(2), Fraction(1), 4, Fraction(1, 2), 0, 0)
    assert rho == 1 and target == 4
    rho, target = vtrace_step(Fraction(1, 2), Fraction(1), 4, Fraction(1), 2, 6)
    assert rho == Fraction(1, 2) and target == 6
    probability, chosen = replay_parts([1, 3, 2], 1)
    assert probability == Fraction(1, 2) and chosen == 2
    clipped = clip_rewards([5, -4, 1], 2)
    assert clipped == [2, -2, 1]
    assert discounted(clipped, Fraction(1, 2)) == Fraction(5, 4)
    mae, sae = absolute_errors([1, 3], [1, 0])
    assert sae == 3 and mae == Fraction(3, 2)
    index, intersection, union = jaccard_parts([1, 0, 1, 0], [1, 1, 0, 0])
    assert intersection == 1 and union == 3 and index == Fraction(1, 3)
    reciprocal, rank = reciprocal_rank([0, 0, 1, 0])
    assert rank == 3 and reciprocal == Fraction(1, 3)
    assert subarray_count([1, 1, 1], 2) == 2
    assert subarray_count([1, -1, 1], 1) == _brute_subarrays([1, -1, 1], 1) == 3
    assert isqrt_pair(10) == (3, 1)
    assert isqrt_pair(16) == (4, 0)
    assert isqrt_pair(0) == (0, 0)
    assert max_product([2, 3, -2, 4]) == _brute_product([2, 3, -2, 4]) == 6
    assert max_product([-2, 3, -4]) == 24
    assert max_product([-2, 0, -1]) == 0
    assert doppler_observed(8, 10, 2, 3) == 13
    assert hubble_speed(4, 3) == 12
    assert fall_height(3) == 45
