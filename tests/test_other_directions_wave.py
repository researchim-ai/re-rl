"""Волна вне графов: RL, машинное обучение, физика и остальная математика."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.discounted_return_task import discounted
from re_rl.tasks.rl.double_q_task import double_q_target
from re_rl.tasks.rl.polyak_task import polyak
from re_rl.tasks.ml.decision_stump_task import stump_errors
from re_rl.tasks.ml.brier_task import brier_score
from re_rl.tasks.math.geometry.pick_theorem_task import pick_area
from re_rl.tasks.math.logic.trapping_rain_task import trap
from re_rl.tasks.math.logic.majority_task import majority
from re_rl.tasks.math.discrete.euclid_task import euclid
from re_rl.tasks.physics.waves.wave_relation_task import wave_speed
from re_rl.tasks.physics.thermodynamics.sensible_heat_task import heat_quantity
from re_rl.tasks.physics.electricity.resistor_pair_task import pair_resistance

WAVE = [
    "reward_to_go", "double_q", "polyak_update",
    "decision_stump", "brier_score",
    "pick_theorem", "trapping_rain", "majority_element", "euclid_gcd",
    "wave_relation", "sensible_heat", "resistor_pair",
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
    assert discounted([1, 2, 4], Fraction(1, 2)) == 3
    assert discounted([1, 2, 4][1:], Fraction(1, 2)) == 4
    action, target = double_q_target([1, 5, 5], [0, 4, 9], 1, Fraction(1, 2))
    assert action == 2 and target == 3
    assert polyak(3, 1, Fraction(1, 2)) == 2
    assert stump_errors([(0, 0), (1, 0), (2, 1), (3, 1)]) == 0
    assert stump_errors([(0, 1), (1, 0), (2, 1)]) == 1
    assert brier_score([(Fraction(1, 2), 1), (Fraction(1, 2), 0)]) == Fraction(1, 4)
    assert pick_area(4, 6) == 6
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert majority([7, 7, 7, 1, 2]) == 7
    assert euclid(48, 18) == (6, 3)
    assert wave_speed(4, 3) == 12
    assert heat_quantity(2, 3, 4) == 24
    series, parallel = pair_resistance(2, 4)
    assert series == 6 and parallel == Fraction(4, 3)
