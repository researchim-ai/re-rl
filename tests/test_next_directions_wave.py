"""Следующая волна: след, Expected SARSA, GAE, MSE, precision@k,
Иосиф, гистограмма, знаки, Коллатц, приведённая масса, циклотрон и красное смещение."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.eligibility_task import accumulating_trace
from re_rl.tasks.rl.expected_sarsa_task import uniform_backup
from re_rl.tasks.rl.gae_task import gae_advantage, td_delta
from re_rl.tasks.ml.mse_task import squared_errors
from re_rl.tasks.ml.precision_at_k_task import topk_hits
from re_rl.tasks.math.discrete.josephus_task import josephus
from re_rl.tasks.math.logic.histogram_task import largest_rectangle
from re_rl.tasks.math.logic.target_sum_task import target_ways
from re_rl.tasks.math.discrete.collatz_task import collatz
from re_rl.tasks.physics.mechanics.reduced_mass_task import reduced_pair
from re_rl.tasks.physics.magnetism.cyclotron_task import cyclotron_omega
from re_rl.tasks.physics.astrophysics.redshift_task import redshift_parts

WAVE = [
    "eligibility_trace", "expected_sarsa", "gae_advantage",
    "mse_loss", "precision_at_k",
    "josephus", "histogram_area", "target_sum", "collatz_steps",
    "reduced_mass", "cyclotron", "spectral_redshift",
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
    assert accumulating_trace([2, 4], Fraction(1, 2), Fraction(1, 2), 0) == [Fraction(3, 2), Fraction(1)]
    mean, target = uniform_backup([2, 4, 6], 1, Fraction(1, 2))
    assert mean == 4 and target == 3
    assert td_delta([2, 2], [0, 0, 0], Fraction(1, 2), 0) == 2
    assert gae_advantage([2, 2], [0, 0, 0], Fraction(1, 2), Fraction(1, 2), 0) == Fraction(5, 2)
    mse, sse = squared_errors([1, 2], [1, 4])
    assert sse == 4 and mse == 2
    assert topk_hits([5, 1, 5], [0, 1, 1], 2) == 1
    assert topk_hits([3, 1, 2], [1, 0, 1], 2) == 2
    survivor, eliminated = josephus(5, 2)
    assert survivor == 3 and eliminated == [2, 4, 1, 5]
    assert josephus(1, 3)[0] == 1
    assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle([2, 2, 2]) == 6
    assert target_ways([1, 1, 1, 1, 1], 3) == 5
    assert collatz(6) == (8, 16)
    assert collatz(1) == (0, 1)
    reduced, reciprocal = reduced_pair(2, 4)
    assert reduced == Fraction(4, 3) and reciprocal == Fraction(3, 4)
    assert cyclotron_omega(2, 3, 4) == Fraction(3, 2)
    z, observed = redshift_parts(4, 2)
    assert z == Fraction(1, 2) and observed == 6
