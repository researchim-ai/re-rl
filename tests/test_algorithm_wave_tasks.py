"""Длинные алгоритмы: SARSA, expectimax, минимакс, Витерби, вывод в цепочке,
локальное выравнивание, Нуссинов и оптимальное дерево поиска."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.rl.sarsa_trajectory_task import apply_sarsa
from re_rl.tasks.rl.q_trajectory_task import apply_q_trajectory
from re_rl.tasks.math.logic.expectimax_task import expectimax
from re_rl.tasks.math.logic.minimax_tree_task import minimax_tree
from re_rl.tasks.ml.hmm_task import forward_probability, viterbi_path
from re_rl.tasks.ml.elimination_task import chain_answers
from re_rl.tasks.math.logic.local_alignment_task import local_alignment
from re_rl.tasks.math.logic.sequence_alignment_task import alignment_score
from re_rl.tasks.math.logic.nussinov_task import brute_pairs, nussinov
from re_rl.tasks.math.logic.optimal_bst_task import optimal_bst

WAVE = [
    "sarsa_trajectory", "expectimax", "minimax_tree", "hmm_decode",
    "elimination_query", "local_alignment", "nussinov", "optimal_bst",
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
        task = gen(task_type=sub, language="ru", difficulty=4)
        text = str(task.final_answer).strip()
        if "," in text and re.fullmatch(r"-?\d+(?:,\s*-?\d+)+", text):
            parts = [int(x) for x in text.replace(" ", "").split(",")]
            wrong = ", ".join(str(x + 3) for x in parts)
        elif re.fullmatch(r"-?\d+", text):
            wrong = str(int(text) + 9)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_answers():
    sarsa = apply_sarsa(1, 2, [(0, 0, 5, 0, 0), (0, 1, 0, 0, 1)], Fraction(1), Fraction(1))
    qlearn = apply_q_trajectory(1, 2, [(0, 0, 5, 0), (0, 1, 0, 0)], Fraction(1), Fraction(1))
    assert sarsa[0][0] == 5 and sarsa[0][1] == 0
    assert qlearn[0][1] == 5
    value, action = expectimax([
        [(Fraction(1, 2), 4), (Fraction(1, 2), 0)],
        [(Fraction(1, 1), 3)],
    ])
    assert value == 3 and action == 2
    assert minimax_tree([[3, 5], [4, 1]]) == (3, 1)
    assert minimax_tree([[1, 9], [2, 2]]) == (2, 2)
    half = Fraction(1, 2)
    start = [half, half]
    trans = [[half, half], [half, half]]
    emit = [[half, half], [half, half]]
    assert forward_probability(start, trans, emit, [0, 0]) == Fraction(1, 4)
    assert viterbi_path(start, trans, emit, [0, 0]) == [0, 0]
    assert chain_answers(Fraction(1, 2), [(Fraction(1), Fraction(0)), (Fraction(1), Fraction(0))]) == (
        Fraction(1, 2), Fraction(1))
    assert local_alignment("AC", "AC") == 2
    assert local_alignment("AAA", "TTT") == 0
    assert alignment_score("AAA", "TTT") == -3
    assert optimal_bst([3, 1]) == 5
    assert optimal_bst([1, 1, 1]) == 5
    for seq in ("AAAUUU", "GCGC", "GCGCGC", "ACGUACGU", "GGGAAAUCC"):
        assert nussinov(seq) == brute_pairs(seq)
    random.seed(0)
    for _ in range(12):
        seq = "".join(random.choice("ACGU") for _ in range(8))
        assert nussinov(seq) == brute_pairs(seq)
