"""Волна для претрейна, SFT и RL: отдача, Q-learning, Беллман,
Кадане, грабитель, стержень, пары, куча, взвешенные интервалы,
периоды полураспада, закон Фурье и энергия пружины."""

import random
import re

import pytest
from fractions import Fraction

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.discounted_return_task import discounted
from re_rl.tasks.rl.q_learning_task import q_update
from re_rl.tasks.math.logic.max_subarray_task import kadane
from re_rl.tasks.math.logic.house_robber_task import rob
from re_rl.tasks.math.logic.rod_cutting_task import rod_profit
from re_rl.tasks.math.logic.pair_sum_task import count_pairs
from re_rl.tasks.math.logic.heap_task import heapify, sift_down
from re_rl.tasks.math.logic.weighted_interval_task import max_weighted

WAVE = [
    "discounted_return", "q_learning", "bellman_backup",
    "max_subarray", "house_robber", "rod_cutting", "pair_sum", "heap_array",
    "weighted_interval", "half_life_steps", "fourier_conduction", "spring_energy",
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
        fa = str(task.final_answer).strip()
        low = fa.lower()
        if low in ("a", "b", "да", "yes"):
            wrong = "B" if low == "a" else "A"
        elif low in ("нет", "no"):
            wrong = "да"
        elif re.fullmatch(r"-?\d+", fa):
            wrong = str(int(fa) + 9)
        elif "," in fa:
            parts = [int(x) for x in fa.replace(" ", "").split(",") if x]
            wrong = ", ".join(str(x + 4) for x in parts)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_rl_and_dp():
    assert discounted([1, 2, 4], Fraction(1, 2)) == 3
    assert discounted([1, 2], Fraction(1, 2), bootstrap=4) == Fraction(1) + 1 + 1
    new_q, delta = q_update(2, Fraction(1, 2), 4, Fraction(1, 2), 2)
    assert delta == 3 and new_q == Fraction(7, 2)
    assert kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rod_profit([0, 1, 5, 8, 9]) == 10
    assert count_pairs([1, 5, 7, -1], 6) == 2
    assert heapify([1, 3, 2]) == [3, 1, 2]
    broken = [1, 3, 2]
    sift_down(broken, 0)
    assert broken == [3, 1, 2]
    assert max_weighted([(0, 2, 5), (1, 3, 10)]) == 10
    assert max_weighted([(0, 1, 5), (1, 2, 7)]) == 12
