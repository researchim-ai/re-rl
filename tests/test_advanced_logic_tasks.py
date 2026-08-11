"""Семантические тесты для волны «графы / оптимизация / симуляция / сетки /
дедукция / игры / пространство» (42 типа).

Проверяем регистрацию, самосогласованность (эталонный ответ засчитывается) и
отклонение заведомо неверного/бессмысленного ответа.
"""

import random

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry

ADV_TYPES = [
    # графы / оптимизация
    "weighted_shortest_path", "topological_sort", "graph_coloring", "mst_weight",
    "eulerian_path", "hamiltonian_path", "bipartite_matching", "tsp", "max_flow",
    "dag_longest_path", "knapsack", "subset_sum",
    # формальная логика / вычисления
    "truth_table", "model_counting", "three_sat", "logical_equivalence", "qbf",
    "dfa_simulation", "turing_machine", "game_of_life", "elementary_ca",
    "rpn_eval", "balanced_brackets", "sorting_trace",
    # сетки
    "nonogram", "binary_puzzle", "hitori", "star_battle", "battleship",
    # дедукция / игры
    "logic_grid", "seating_circular", "tournament", "combinatorial_games", "tic_tac_toe",
    # пространство / прочее
    "cube_net", "dice_reasoning", "rotation_reflection", "paper_folding",
    "cipher_decode", "pigeonhole", "monty_hall", "allen_relations",
    # продвинутый ризонинг
    "arc_grid_induction", "program_trace", "sprague_grundy", "natural_deduction",
    "edit_distance", "calendar_reasoning", "word_ladder", "cfg_membership",
]


@pytest.mark.parametrize("task_type", ADV_TYPES)
def test_registered(task_type):
    assert task_type in ALL_TASK_GENERATORS
    assert task_type in registry


@pytest.mark.parametrize("task_type", ADV_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
def test_self_consistency(task_type, language):
    for difficulty in (1, 3, 5, 7, 10):
        for seed in range(5):
            random.seed(seed * 100 + difficulty)
            task = ALL_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
            assert task.description
            assert len(task.solution_steps) >= 1
            assert task.final_answer is not None
            got = task.verify(f"<answer>{task.final_answer}</answer>")
            assert got == pytest.approx(1.0), (task_type, language, difficulty, task.final_answer)


@pytest.mark.parametrize("task_type", ADV_TYPES)
def test_wrong_answer_rejected(task_type):
    random.seed(11)
    for _ in range(8):
        task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=5)
        assert task.verify("<answer>абракадабра фубар нечто</answer>") < 1.0


def test_three_sat_alternative_assignment():
    """Любой выполняющий набор должен засчитываться, не только эталонный."""
    from itertools import product
    random.seed(3)
    for _ in range(20):
        t = ALL_TASK_GENERATORS["three_sat"](language="ru", difficulty=6)
        for bits in product((0, 1), repeat=t.nv):
            if t._satisfies(list(bits)):
                ans = " ".join(map(str, bits))
                assert t.verify(f"<answer>{ans}</answer>") == pytest.approx(1.0)


def test_tic_tac_toe_any_optimal_move_accepted():
    random.seed(5)
    for _ in range(20):
        t = ALL_TASK_GENERATORS["tic_tac_toe"](language="ru", difficulty=4, subtype="best_move")
        for cell in t._best_moves():
            assert t.verify(f"<answer>{cell + 1}</answer>") == pytest.approx(1.0)
