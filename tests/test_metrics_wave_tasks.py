"""Волна метрик и точных отношений: PPO, важность выборки, средняя награда,
каппа, R^2, средняя точность, много сделок, квадраты, палиндром,
фактор Лоренца, светимость и энергия катушки."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.ppo_task import ppo_clip
from re_rl.tasks.rl.importance_task import importance_product
from re_rl.tasks.rl.average_reward_task import average_reward_parts
from re_rl.tasks.ml.kappa_task import cohen_parts
from re_rl.tasks.ml.r2_task import r2_parts
from re_rl.tasks.ml.average_precision_task import average_precision
from re_rl.tasks.math.logic.stock_unlimited_task import unlimited_profit
from re_rl.tasks.math.discrete.min_squares_task import min_squares
from re_rl.tasks.math.logic.palindrome_subseq_task import lps_length
from re_rl.tasks.physics.relativity.rational_gamma_task import lorentz_factor, proper_time
from re_rl.tasks.physics.thermodynamics.stefan_ratio_task import luminosity_parts
from re_rl.tasks.physics.electricity.inductor_energy_task import inductor_energy

WAVE = [
    "ppo_clip", "importance_ratio", "average_reward",
    "cohen_kappa", "r2_score", "mean_average_precision",
    "stock_unlimited", "min_squares", "palindrome_subseq",
    "rational_gamma", "stefan_ratio", "inductor_energy",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


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
        fa = str(task.final_answer).strip().lower()
        if fa in ("да", "yes"):
            wrong = "нет"
        elif fa in ("нет", "no"):
            wrong = "да"
        elif re.fullmatch(r"-?\d+", str(task.final_answer).strip()):
            wrong = str(int(task.final_answer) + 9)
        elif "," in str(task.final_answer):
            parts = [int(x) for x in str(task.final_answer).replace(" ", "").split(",")]
            wrong = ", ".join(str(x + 3) for x in parts)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_answers():
    clipped, surrogate = ppo_clip(Fraction(2), Fraction(1, 2), 4)
    assert clipped == Fraction(3, 2) and surrogate == 6
    clipped, surrogate = ppo_clip(Fraction(2), Fraction(1, 2), -4)
    assert clipped == Fraction(3, 2) and surrogate == -8
    product, above = importance_product([(1, 2), (3, 1), (2, 2)])
    assert product == Fraction(3, 2) and above == 1
    mean, delta = average_reward_parts([1, 3], [0, 0, 0], 0)
    assert mean == 2 and delta == -1
    assert cohen_parts(2, 0, 0, 2) == (1, 1)
    assert cohen_parts(1, 1, 1, 1) == (0, Fraction(1, 2))
    assert cohen_parts(1, 0, 0, 0) is None
    r2, ss_tot, ss_res = r2_parts([1, 2, 3], [2, 2, 2])
    assert ss_tot == 2 and ss_res == 2 and r2 == 0
    assert r2_parts([1, 2, 3], [1, 2, 3])[0] == 1
    ap, last = average_precision([1, 0, 1])
    assert ap == Fraction(5, 6) and last == Fraction(2, 3)
    assert unlimited_profit([7, 1, 5, 3, 6, 4]) == 7
    assert unlimited_profit([4, 3, 2]) == 0
    assert min_squares(12) == 3
    assert min_squares(13) == 2
    assert min_squares(1) == 1
    assert lps_length("bbbab") == 4
    assert lps_length("cbbd") == 2
    assert lps_length("a") == 1
    assert lorentz_factor(3, 5, 4) == Fraction(5, 4)
    assert proper_time(5, 5, 4) == 4
    ratio, hot = luminosity_parts(2, 2)
    assert ratio == 16 and hot == 4
    assert inductor_energy(2, 3) == 9
    assert inductor_energy(1, 1) == Fraction(1, 2)
