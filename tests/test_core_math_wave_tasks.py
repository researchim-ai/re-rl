"""Семантические тесты для «важной математики» (волна из 25 типов).

Проверяем не только самосогласованность (эталон засчитывается), но и то, что
принимаются эквивалентные формы ответа, а неверные ответы отвергаются.
"""

import math
import random

import numpy as np
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS


def _seed(s=0):
    random.seed(s)
    np.random.seed(s)


NEW_TYPES = [
    "taylor_series", "partial_fractions", "partial_derivatives", "area_between_curves",
    "lhopital", "recurrence", "prime_factorization", "diophantine", "modular_inverse",
    "continued_fraction", "generating_function", "gaussian_elimination",
    "matrix_multiplication", "gram_schmidt", "least_squares", "roots_of_unity",
    "expected_value", "markov_chain", "conditional_probability", "hypothesis_testing",
    "coordinate_geometry", "shoelace_area", "triangle_solving", "conic_sections", "vieta",
]


@pytest.mark.parametrize("task_type", NEW_TYPES)
def test_registered_and_solvable(task_type):
    _seed(1)
    task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=4)
    assert task.final_answer is not None
    assert len(task.solution_steps) >= 1
    assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


@pytest.mark.parametrize("task_type", NEW_TYPES)
def test_wrong_answer_rejected(task_type):
    _seed(2)
    task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=4)
    # Заведомо неверный ответ должен получить оценку < 1.
    assert task.verify("<answer>совершенно неверный ответ 123456789.987</answer>") < 1.0


def test_prime_factorization_flat_form():
    _seed(3)
    from re_rl.tasks.math.discrete.prime_factorization_task import PrimeFactorizationTask
    task = PrimeFactorizationTask.generate_random_task(language="en", difficulty=5)
    flat = " * ".join(str(p) for p in sorted(sp_factors(task.n)))
    assert task.verify(f"<answer>{flat}</answer>") == pytest.approx(1.0)
    assert task.verify("<answer>2 * 3</answer>") < 1.0 or task.n == 6


def sp_factors(n):
    import sympy as sp
    fs = []
    for base, exp in sp.factorint(n).items():
        fs.extend([base] * exp)
    return fs


def test_diophantine_alternative_solution():
    _seed(4)
    from re_rl.tasks.math.discrete.diophantine_task import DiophantineTask
    task = DiophantineTask.generate_random_task(language="ru", difficulty=6)
    g = math.gcd(task.a, task.b)
    x2 = task.x_sol + task.b // g
    y2 = task.y_sol - task.a // g
    assert task.a * x2 + task.b * y2 == task.c
    assert task.verify(f"<answer>x={x2}, y={y2}</answer>") == pytest.approx(1.0)


def test_modular_inverse_shifted_representative():
    _seed(5)
    from re_rl.tasks.math.discrete.modular_inverse_task import ModularInverseTask
    task = ModularInverseTask.generate_random_task(language="ru", difficulty=5)
    shifted = task._inv + task.m
    assert task.verify(f"<answer>{shifted}</answer>") == pytest.approx(1.0)


def test_gram_schmidt_scaled_basis_accepted():
    _seed(6)
    from re_rl.tasks.math.linear_algebra.gram_schmidt_task import GramSchmidtTask
    task = GramSchmidtTask.generate_random_task(language="ru", difficulty=6)
    scaled = ", ".join(
        "(" + ", ".join(str(3 * v[i]) for i in range(v.rows)) + ")" for v in task._ortho
    )
    assert task.verify(f"<answer>{scaled}</answer>") == pytest.approx(1.0)


def test_taylor_series_reordered_terms_accepted():
    _seed(7)
    from re_rl.tasks.math.analysis.taylor_series_task import TaylorSeriesTask
    task = TaylorSeriesTask.generate_random_task(language="en", difficulty=5)
    # Полностью раскрытая (та же) форма и явно неверная.
    import sympy as sp
    same = sp.sstr(sp.expand(task._ref_expr))
    assert task.verify(f"<answer>{same}</answer>") == pytest.approx(1.0)
    assert task.verify("<answer>x + 12345</answer>") < 1.0


def test_conic_and_hypothesis_are_balanced():
    """Оба класса ответов встречаются (нет вырождения в один класс)."""
    kinds = set()
    decisions = set()
    for s in range(40):
        _seed(s)
        c = ALL_TASK_GENERATORS["conic_sections"](language="ru", difficulty=5)
        kinds.add(c.final_answer)
        _seed(s + 100)
        h = ALL_TASK_GENERATORS["hypothesis_testing"](language="ru", difficulty=6)
        decisions.add(h.final_answer)
    assert len(kinds) >= 3
    assert decisions == {"reject", "not reject"}
