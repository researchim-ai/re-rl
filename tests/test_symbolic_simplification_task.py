import random

import sympy as sp

from re_rl.tasks.math.algebra.symbolic_simplification_task import (
    SymbolicSimplificationTask,
)


def test_generation_and_registration():
    from re_rl.tasks.registry import registry
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    assert "symbolic_simplification" in registry
    assert "symbolic_simplification" in ALL_TASK_GENERATORS

    task = SymbolicSimplificationTask.generate_random_task(language="ru", difficulty=5)
    assert task.description
    assert task.final_answer
    assert task.solution_steps


def test_verify_accepts_self_answer():
    random.seed(42)
    for difficulty in range(1, 11):
        task = SymbolicSimplificationTask.generate_random_task(difficulty=difficulty)
        assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


def test_verify_accepts_equivalent_form():
    task = SymbolicSimplificationTask(difficulty=4, num_factors=2, num_vars=1, extra_terms=0)
    task.solve()
    # Эквивалентная (нераскрытая) форма исходного выражения должна засчитываться.
    factored = task._format_expr(task._raw_expr)
    assert task.verify(f"<answer>{factored}</answer>") == 1.0


def test_verify_rejects_wrong_answer():
    task = SymbolicSimplificationTask.generate_random_task(difficulty=5)
    assert task.verify("<answer>0</answer>") in (0.0,)
    assert task.verify("<answer>this is not math</answer>") == 0.0


def test_bilingual():
    for lang in ("ru", "en"):
        task = SymbolicSimplificationTask.generate_random_task(language=lang, difficulty=3)
        assert task.description
        assert task.verify(str(task.final_answer)) == 1.0
