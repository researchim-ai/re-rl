"""Структуры и схемы: альфа-бета, многочлены, отрезки, дерево,
подпоследовательности, Шамир, PageRank и Double Q."""

import random
import re
from fractions import Fraction

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.logic.alpha_beta_task import alpha_beta
from re_rl.tasks.math.logic.polynomial_product_task import poly_eval, poly_mul
from re_rl.tasks.math.logic.range_add_task import apply_range_adds
from re_rl.tasks.math.logic.tree_mis_task import tree_mis
from re_rl.tasks.math.logic.subsequence_count_task import count_subsequence
from re_rl.tasks.math.discrete.secret_share_task import reconstruct
from re_rl.tasks.ml.pagerank_task import pagerank
from re_rl.tasks.rl.double_q_trajectory_task import apply_double_q

WAVE = [
    "alpha_beta", "polynomial_product", "range_add", "tree_mis",
    "subsequence_count", "secret_share", "pagerank", "double_q_trajectory",
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
        if re.fullmatch(r"-?\d+", text):
            wrong = str(int(text) + 9)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_answers():
    assert alpha_beta([[3, 5], [2, 9]]) == (3, 3)
    assert alpha_beta([[3, 5], [2, 9], [1, 8]]) == (3, 4)
    product = poly_mul([1, 2], [3, 4])
    assert product == [3, 10, 8]
    assert poly_eval(product, 2) == 55
    assert apply_range_adds([1, 2, 3, 4], [(1, 2, 10)], 1, 2) == (25, 30)
    assert tree_mis(3, [(0, 1), (1, 2)]) == 2
    assert tree_mis(4, [(0, 1), (0, 2), (0, 3)]) == 3
    assert tree_mis(1, []) == 1
    assert count_subsequence("rabbbit", "rabbit") == 3
    assert count_subsequence("aaa", "aa") == 3
    assert reconstruct([(1, 1), (2, 4)], 7) == 5
    ranks = pagerank(3, [(0, 1), (1, 2), (2, 0)])
    assert ranks == [Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)]
    mutual = pagerank(2, [(0, 1), (1, 0)])
    assert mutual == [Fraction(1, 2), Fraction(1, 2)]
    tables = apply_double_q(1, 2, [(0, 0, 4, 0, 0), (0, 1, 2, 0, 1)], Fraction(1), Fraction(1))
    assert tables[0][0][0] == 4
    assert tables[1][0][1] == 6
