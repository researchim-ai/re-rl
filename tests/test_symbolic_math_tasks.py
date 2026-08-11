"""Тесты новых символьных/z3-верифицируемых математических задач."""

import random

import sympy as sp

from re_rl.tasks.math.logic.cryptarithmetic_task import CryptarithmeticTask
from re_rl.tasks.math.analysis.symbolic_regression_task import SymbolicRegressionTask
from re_rl.tasks.math.algebra.polynomial_factorization_task import PolynomialFactorizationTask
from re_rl.tasks.math.discrete.base_conversion_task import BaseConversionTask, to_base
from re_rl.tasks.math.linear_algebra.matrix_reasoning_task import MatrixReasoningTask
from re_rl.tasks.math.logic.inequality_proof_task import InequalityProofTask
from re_rl.tasks.math.discrete.modular_arithmetic_task import ModularArithmeticTask


def test_all_registered():
    from re_rl.tasks.registry import registry
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    for t in (
        "cryptarithmetic", "symbolic_regression", "polynomial_factorization",
        "base_conversion", "matrix_reasoning", "inequality_proof", "modular_arithmetic",
    ):
        assert t in registry and t in ALL_TASK_GENERATORS


# --------------------------- cryptarithmetic ---------------------------

def test_cryptarithmetic_valid_and_invalid():
    random.seed(1)
    for _ in range(20):
        task = CryptarithmeticTask.generate_random_task(difficulty=4)
        assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    # Все нули — заведомо неверно (нарушает биекцию / ведущие цифры).
    task = CryptarithmeticTask.generate_random_task(difficulty=3)
    zero = ",".join(f"{l}=0" for l in set(task._word_a + task._word_b + task._word_c))
    assert task.verify(f"<answer>{zero}</answer>") == 0.0


# --------------------------- symbolic_regression ---------------------------

def test_symbolic_regression_equivalent_forms():
    random.seed(2)
    task = SymbolicRegressionTask.generate_random_task(difficulty=3)
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    # Неверная функция не проходит.
    assert task.verify("<answer>x + 12345</answer>") == 0.0


# --------------------------- polynomial_factorization ---------------------------

def test_polynomial_factorization_equivalence():
    random.seed(3)
    task = PolynomialFactorizationTask.generate_random_task(difficulty=4)
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    # Развёрнутая форма эквивалентна и тоже засчитывается.
    expanded = sp.sstr(task._expanded).replace("**", "^")
    assert task.verify(f"<answer>{expanded}</answer>") == 1.0
    assert task.verify("<answer>x - 999</answer>") == 0.0


# --------------------------- base_conversion ---------------------------

def test_base_conversion_value():
    assert to_base(19, 2) == "10011" or to_base(19, 2) == "10011"
    assert int(to_base(255, 16), 16) == 255
    random.seed(4)
    task = BaseConversionTask.generate_random_task(difficulty=4, subtype="convert")
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


def test_bitwise_value():
    task = BaseConversionTask.generate_random_task(difficulty=5, subtype="bitwise")
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


# --------------------------- matrix_reasoning ---------------------------

def test_matrix_determinant_and_eigenvalues():
    random.seed(5)
    det_task = MatrixReasoningTask.generate_random_task(difficulty=5, subtype="determinant")
    assert det_task.verify(f"<answer>{det_task.final_answer}</answer>") == 1.0

    eig_task = MatrixReasoningTask.generate_random_task(difficulty=6, subtype="eigenvalues")
    assert eig_task.verify(f"<answer>{eig_task.final_answer}</answer>") == 1.0
    # Порядок собственных значений не важен.
    reversed_ans = ", ".join(reversed(str(eig_task.final_answer).split(", ")))
    assert eig_task.verify(f"<answer>{reversed_ans}</answer>") == 1.0


# --------------------------- inequality_proof ---------------------------

def test_inequality_proof_decision():
    # (x)^2 + 0*x + 1 >= 0 всегда истинно -> YES.
    task = InequalityProofTask(difficulty=3, max_coeff=5)
    task.a, task.b, task.c = 1, 0, 1
    task._always_nonneg = task._decide()
    task.solve()
    assert task.final_answer == "YES"
    assert task.verify("<answer>YES</answer>") == 1.0

    # x^2 - 4 имеет отрицательные значения -> NO.
    task2 = InequalityProofTask(difficulty=3)
    task2.a, task2.b, task2.c = 1, 0, -4
    task2._always_nonneg = task2._decide()
    task2.solve()
    assert task2.final_answer == "NO"


def test_inequality_both_classes():
    random.seed(0)
    labels = {InequalityProofTask.generate_random_task(difficulty=5).final_answer for _ in range(40)}
    assert labels == {"YES", "NO"}


# --------------------------- modular_arithmetic ---------------------------

def test_modexp_value():
    task = ModularArithmeticTask.generate_random_task(difficulty=3, subtype="modexp")
    assert int(task.final_answer) == pow(task.a, task.b, task.m)
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


def test_discrete_log_accepts_equivalent_exponent():
    random.seed(6)
    task = ModularArithmeticTask.generate_random_task(difficulty=5, subtype="discrete_log")
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    # Показатель + (p-1) даёт то же значение по малой теореме Ферма (порядок делит p-1).
    equiv = int(task.final_answer) + (task.p - 1)
    assert task.verify(f"<answer>{equiv}</answer>") == 1.0
