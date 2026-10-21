"""Большая волна: Каталан, Стирлинг, Грей, двоичный поиск, цепочка матриц,
общая подстрока, объёмы, физика удара и встречи, RR, дедлок, аукцион, Шепли,
шарнирная потеря, косинус и одномерная регрессия."""

import random
import re

import pytest
from fractions import Fraction

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.discrete.catalan_task import catalan_sequence
from re_rl.tasks.math.discrete.stirling_task import stirling_row
from re_rl.tasks.math.discrete.gray_code_task import gray_encode, gray_decode
from re_rl.tasks.math.logic.binary_search_task import binary_search
from re_rl.tasks.math.logic.matrix_chain_task import matrix_chain_cost
from re_rl.tasks.math.logic.common_substring_task import longest_common_substring
from re_rl.tasks.math.logic.round_robin_task import round_robin
from re_rl.tasks.math.logic.deadlock_task import nodes_on_cycles
from re_rl.tasks.math.logic.second_price_task import second_price
from re_rl.tasks.math.logic.shapley_task import shapley
from re_rl.tasks.ml.cosine_task import prefer
from re_rl.tasks.ml.univariate_regression_task import fit
from re_rl.tasks.ml.hinge_task import hinge_one

BROAD_TYPES = [
    "catalan", "stirling_second", "gray_code", "binary_search", "matrix_chain",
    "common_substring", "solid_volume", "internal_resistance", "restitution",
    "meeting_motion", "lc_oscillator", "stellar_parallax", "round_robin", "deadlock",
    "second_price", "shapley_value", "hinge_loss", "cosine_rank", "univariate_regression",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


@pytest.mark.parametrize("task_type", BROAD_TYPES)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", BROAD_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(2):
            _seed(task_type, sub, language, difficulty, i)
            task = gen(task_type=sub, language=language, difficulty=difficulty)
            assert task.final_answer is not None
            assert "{" not in task.description and "}" not in task.description
            assert task.solution_steps
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", BROAD_TYPES)
def test_wrong_answer_rejected(task_type):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        _seed("bad", task_type, sub)
        task = gen(task_type=sub, language="ru", difficulty=6)
        fa = str(task.final_answer).strip()
        low = fa.lower()
        if low in ("да", "yes", "a"):
            wrong = "нет" if low != "a" else "B"
        elif low in ("нет", "no", "b"):
            wrong = "да" if low != "b" else "A"
        elif re.fullmatch(r"-?\d+", fa):
            wrong = str(int(fa) + 9)
        elif re.fullmatch(r"[01]+", fa):
            wrong = "1" + fa
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_formulas():
    assert catalan_sequence(5)[-1] == 42
    assert stirling_row(4)[2] == 7
    assert sum(stirling_row(5)) == 52
    assert gray_encode(2) == 3 and gray_decode(3) == 2
    assert gray_decode(gray_encode(13)) == 13
    idx, comps, _ = binary_search([1, 3, 5, 7, 9], 7)
    assert idx == 3 and comps == 2
    assert matrix_chain_cost([2, 3, 4]) == 24
    assert longest_common_substring("ababc", "babca") == 4
    wait, turn, finish = round_robin([4, 1], 2)
    assert finish == [5, 3] and wait == 3 and turn == 8
    assert nodes_on_cycles(2, [(0, 1), (1, 0)]) == {0, 1}
    assert nodes_on_cycles(2, [(0, 1)]) == set()
    assert nodes_on_cycles(1, [(0, 0)]) == {0}
    assert second_price([5, 3, 5]) == (1, 5)
    values = {
        frozenset(): 0,
        frozenset([0]): 0, frozenset([1]): 0, frozenset([2]): 0,
        frozenset([0, 1]): 0, frozenset([0, 2]): 0, frozenset([1, 2]): 0,
        frozenset([0, 1, 2]): 6,
    }
    assert shapley(values, 0) == 2
    assert hinge_one(0, 0, 0, (0, 0, 1)) == 1
    assert prefer((1, 0), (1, 0), (0, 1)) == "A"
    assert prefer((1, 0), (-1, 0), (-1, 1)) == "B"
    slope, intercept = fit([(1, 2), (2, 4)])
    assert slope == 2 and intercept == 0
    assert Fraction(4 * 27, 3) == 36
