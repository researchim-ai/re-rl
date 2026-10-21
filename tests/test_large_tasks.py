"""Крупные многошаговые задачи: горизонт, траектория Q, назначение, Флойд,
выравнивание, запросы к массиву, Калман и смешанное равновесие."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.finite_horizon_task import finite_horizon
from re_rl.tasks.rl.q_trajectory_task import apply_q_trajectory, greedy_action
from re_rl.tasks.math.logic.min_assignment_task import min_assignment
from re_rl.tasks.math.logic.floyd_distance_task import floyd_stats
from re_rl.tasks.math.logic.sequence_alignment_task import alignment_score
from re_rl.tasks.math.logic.range_query_task import apply_updates
from re_rl.tasks.ml.kalman_task import kalman_filter
from re_rl.tasks.math.logic.mixed_nash_task import mixed_equilibrium

WAVE = [
    "finite_horizon", "q_trajectory", "min_assignment", "floyd_distance",
    "sequence_alignment", "range_query", "kalman_update", "mixed_nash",
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
        if re.fullmatch(r"-?\d+", str(task.final_answer).strip()):
            wrong = str(int(task.final_answer) + 9)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_answers():
    values, actions = finite_horizon([[1, 0], [0, 5]], [[1, 0], [0, 1]], 2, Fraction(1))
    assert values == [6, 10]
    assert actions == [1, 2]
    table = apply_q_trajectory(1, 2, [(0, 0, 4, 0), (0, 1, 0, 0)], Fraction(1), Fraction(1, 2))
    assert table[0][0] == 4 and table[0][1] == 2
    assert greedy_action(table[0]) == 1
    cost, perm = min_assignment([[9, 2, 7], [6, 4, 3], [5, 8, 1]])
    assert cost == 9 and perm == (1, 0, 2)
    cost, perm = min_assignment([[1, 2], [3, 4]])
    assert cost == 5 and perm == (0, 1)
    total, diameter = floyd_stats(3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)])
    assert total == 9 and diameter == 2
    assert alignment_score("AC", "AC") == 2
    assert alignment_score("AA", "A") == 0
    assert alignment_score("A", "T") == -1
    assert apply_updates([1, 2, 3, 4], [(1, 10)], 0, 3) == (18, 18)
    assert apply_updates([1, 2, 3, 4], [(1, 10)], 1, 2) == (13, 18)
    mean, variance = kalman_filter(0, 1, [(2, 1), (2, 1)])
    assert mean == Fraction(4, 3) and variance == Fraction(1, 3)
    assert mixed_equilibrium([[1, -1], [-1, 1]], [[-1, 1], [1, -1]]) == (Fraction(1, 2), Fraction(1, 2))
    assert mixed_equilibrium([[2, 0], [0, 1]], [[1, 0], [0, 2]]) == (Fraction(2, 3), Fraction(1, 3))
