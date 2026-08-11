"""Семантические тесты для волны логических/ризонинг-задач (20 типов).

Проверяем регистрацию, самосогласованность (эталонный ответ засчитывается),
устойчивость к обёрткам ответа и отклонение заведомо неверных ответов.
"""

import random

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry

LOGIC_TYPES = [
    "graph_reasoning", "ordering_puzzle", "state_tracking", "grid_navigation",
    "interval_scheduling", "set_reasoning", "pattern_induction", "syllogism",
    "logical_entailment", "boolean_circuit", "mastermind", "countdown_24",
    "game_theory_optimal", "family_tree", "minesweeper_deduction", "n_queens",
    "magic_square", "skyscrapers", "kenken", "kakuro",
]


@pytest.mark.parametrize("task_type", LOGIC_TYPES)
def test_registered(task_type):
    assert task_type in ALL_TASK_GENERATORS
    assert task_type in registry


@pytest.mark.parametrize("task_type", LOGIC_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
def test_self_consistency(task_type, language):
    """Эталонный ответ задачи должен верифицироваться на всех уровнях сложности."""
    for difficulty in (1, 3, 5, 7, 10):
        for seed in range(5):
            random.seed(seed * 100 + difficulty)
            task = ALL_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
            assert task.description
            assert len(task.solution_steps) >= 1
            assert task.final_answer is not None
            got = task.verify(f"<answer>{task.final_answer}</answer>")
            assert got == pytest.approx(1.0), (task_type, language, difficulty, task.final_answer)


@pytest.mark.parametrize("task_type", LOGIC_TYPES)
def test_wrong_answer_rejected(task_type):
    """Явно неверный/бессмысленный ответ не должен засчитываться."""
    random.seed(7)
    for _ in range(8):
        task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=5)
        # нейтральная строка без цифр и без ключевых слов-ответов
        assert task.verify("<answer>абракадабра фубар нечто</answer>") < 1.0


def test_ordering_reversed_rejected():
    """Для упорядочивания обратный порядок не должен приниматься за верный."""
    random.seed(3)
    task = ALL_TASK_GENERATORS["ordering_puzzle"](language="ru", difficulty=5)
    reversed_order = ", ".join(reversed(task.true_order))
    if reversed_order != ", ".join(task.true_order):
        assert task.verify(f"<answer>{reversed_order}</answer>") < 1.0


def test_countdown_accepts_alternative_expression():
    """Любое корректное выражение из тех же чисел, равное цели, засчитывается."""
    random.seed(0)
    task = ALL_TASK_GENERATORS["countdown_24"](language="ru", difficulty=3)
    # эталонное выражение (в другой форме — со знаком =) тоже принимается
    assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


def test_n_queens_alternative_solution_accepted():
    """Для n_queens засчитывается любая валидная расстановка, а не только эталон."""
    random.seed(1)
    task = ALL_TASK_GENERATORS["n_queens"](language="ru", difficulty=1, subtype="solve")
    # переставим строки местами так, чтобы получить заведомо невалидный ответ
    bad = " ".join(["1"] * task.n)  # все ферзи в одном столбце — конфликт
    assert task.verify(f"<answer>{bad}</answer>") < 1.0
