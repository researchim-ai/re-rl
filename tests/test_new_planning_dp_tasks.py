import random

from re_rl.tasks.math.discrete.dynamic_programming_task import DynamicProgrammingTask
from re_rl.tasks.math.logic.regex_dfa_task import RegexDFATask
from re_rl.tasks.math.planning.blocks_world_task import BlocksWorldTask


def test_registration():
    from re_rl.tasks.registry import registry
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    for t in ("dynamic_programming", "regex_dfa", "blocks_world"):
        assert t in registry
        assert t in ALL_TASK_GENERATORS


# --------------------------- dynamic_programming ---------------------------

def test_dp_grid_paths_value():
    task = DynamicProgrammingTask(difficulty=3, subtype="grid_paths")
    task.solve()
    # Число путей = C(rows+cols-2, rows-1).
    import math
    expected = math.comb(task.rows + task.cols - 2, task.rows - 1)
    assert int(task.final_answer) == expected
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    assert task.verify("<answer>0</answer>") == 0.0


def test_dp_coin_change_value():
    task = DynamicProgrammingTask(difficulty=6, subtype="coin_change", amount=6, num_coins=3)
    task.solve()
    # Проверяем на известном примере: монеты содержат 1 -> хотя бы 1 способ.
    assert int(task.final_answer) >= 1
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


def test_dp_coin_change_known():
    # amount=4, coins=[1,2] -> способы: 1+1+1+1, 1+1+2, 2+2 = 3.
    assert DynamicProgrammingTask._count_coin_change(4, [1, 2]) == 3


# --------------------------- regex_dfa ---------------------------

def test_regex_verify_and_synonyms():
    random.seed(1)
    task = RegexDFATask.generate_random_task(difficulty=4)
    assert task.final_answer in ("YES", "NO")
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    opposite = "нет" if task.final_answer == "YES" else "да"
    assert task.verify(f"<answer>{opposite}</answer>") == 0.0


def test_regex_both_classes():
    random.seed(0)
    labels = {RegexDFATask.generate_random_task(difficulty=5).final_answer for _ in range(40)}
    assert labels == {"YES", "NO"}


# --------------------------- blocks_world ---------------------------

def test_blocks_reference_plan_valid():
    random.seed(2)
    for _ in range(20):
        task = BlocksWorldTask.generate_random_task(difficulty=4)
        assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


def test_blocks_illegal_plan_rejected():
    random.seed(3)
    task = BlocksWorldTask.generate_random_task(difficulty=3)
    # Перемещение блока сам на себя недопустимо.
    assert task.verify("<answer>move A onto A</answer>") == 0.0


def test_blocks_alternative_valid_plan():
    # План, достигающий цели другим путём (через полную разборку на стол),
    # должен засчитываться, даже если он длиннее эталонного.
    random.seed(5)
    task = BlocksWorldTask.generate_random_task(difficulty=3)
    # Собираем план: всё на стол, затем строим целевые стопки снизу вверх.
    moves = []
    # 1) Разбираем все стопки: многократно кладём верхние блоки на стол.
    state = dict(task._init_state)
    changed = True
    while changed:
        changed = False
        for b in task.blocks:
            if state[b] != "table" and task._clear(state, b):
                moves.append(f"move {b} onto table")
                state[b] = "table"
                changed = True
    # 2) Строим целевые стопки: block -> support, снизу вверх.
    goal = task._goal_state
    placed = {b for b in task.blocks if goal[b] == "table"}
    remaining = [b for b in task.blocks if goal[b] != "table"]
    guard = 0
    while remaining and guard < 100:
        guard += 1
        for b in list(remaining):
            if goal[b] in placed:
                moves.append(f"move {b} onto {goal[b]}")
                placed.add(b)
                remaining.remove(b)
    plan = "; ".join(moves)
    assert task.verify(f"<answer>{plan}</answer>") == 1.0
