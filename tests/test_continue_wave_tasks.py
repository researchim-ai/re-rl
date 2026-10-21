"""Продолжение каталога: SARSA, ε-жадный выбор, оценка политики,
путь по сетке, акция, прыжки, вода, декодирование, бензоколонки,
маятник, КПД и относительная скорость."""

import random
import re

import pytest
from fractions import Fraction

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.sarsa_task import sarsa_update
from re_rl.tasks.rl.epsilon_greedy_task import epsilon_choice
from re_rl.tasks.rl.policy_expectation_task import policy_value
from re_rl.tasks.math.logic.min_path_sum_task import min_path_sum
from re_rl.tasks.math.logic.stock_profit_task import max_profit
from re_rl.tasks.math.logic.jump_game_task import min_jumps
from re_rl.tasks.math.logic.container_water_task import max_water
from re_rl.tasks.math.logic.decode_ways_task import num_decodings
from re_rl.tasks.math.logic.gas_station_task import circuit_start

WAVE = [
    "sarsa", "epsilon_greedy", "policy_expectation",
    "min_path_sum", "stock_profit", "jump_game", "container_water",
    "decode_ways", "gas_station", "pendulum_ratio", "mechanical_efficiency",
    "relative_velocity",
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
        task = gen(task_type=sub, language="ru", difficulty=7)
        fa = str(task.final_answer).strip()
        if re.fullmatch(r"-?\d+", fa):
            wrong = str(int(fa) + 8)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_cases():
    new_q, delta = sarsa_update(2, Fraction(1, 2), 4, Fraction(1, 2), 2)
    assert delta == 3 and new_q == Fraction(7, 2)
    # u = 1/4 < ε = 1/2, (u/ε)*3 = 3/2, целая часть 1, номер с 1 равен 2
    assert epsilon_choice([1, 9, 3], Fraction(1, 2), Fraction(1, 4)) == 2
    # u больше ε, жадно берётся действие 2
    assert epsilon_choice([1, 9, 9], Fraction(1, 2), Fraction(3, 4)) == 2
    assert policy_value([1, 1], [2, 4]) == 3
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5
    assert min_jumps([2, 3, 1, 1, 4]) == 2
    assert max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert num_decodings("12") == 2
    assert num_decodings("226") == 3
    assert num_decodings("06") == 0
    assert circuit_start([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert circuit_start([2, 3], [3, 4]) == -1
