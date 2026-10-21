"""Тесты для новой волны ризонинг-задач: datalog_inference, unification,
lambda_calculus, resolution, lis_dp, kmp_matching, sliding_puzzle.

Проверяются: регистрация, самосогласованность (verify своего ответа = 1.0),
отсутствие незаполненных плейсхолдеров, отклонение неверных ответов, а также
точечная корректность базовых алгоритмов (LIS, LPS, префикс-функция KMP,
разрешимость пятнашек, A*)."""

import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.logic.lis_dp_task import LISDPTask
from re_rl.tasks.math.logic.kmp_matching_task import KMPMatchingTask
from re_rl.tasks.math.logic.sliding_puzzle_task import SlidingPuzzleTask
from re_rl.tasks.math.logic.resolution_task import ResolutionTask

NEW_TYPES = [
    "datalog_inference", "unification", "lambda_calculus", "resolution",
    "lis_dp", "kmp_matching", "sliding_puzzle",
    "algorithm_complexity", "twos_complement", "connect_four",
    "computational_geometry", "graph_connectivity", "huffman_coding", "dfa_minimization",
    "stable_matching", "hamming_code", "page_replacement", "tree_queries",
    "os_scheduling", "numerical_methods", "min_coins",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


@pytest.mark.parametrize("task_type", NEW_TYPES)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", NEW_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 3, 5, 7, 10])
def test_self_consistent(task_type, language, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    subs = getattr(cls, "TASK_TYPES", [None])
    for sub in subs:
        for i in range(4):
            _seed(task_type, sub, language, difficulty, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language=language, difficulty=difficulty, **kwargs)
            assert task.final_answer is not None
            assert "{" not in task.description and "}" not in task.description
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", NEW_TYPES)
@pytest.mark.parametrize("difficulty", [2, 6, 10])
def test_wrong_answer_rejected(task_type, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    subs = getattr(cls, "TASK_TYPES", [None])
    for sub in subs:
        for i in range(4):
            _seed("wrong", task_type, sub, difficulty, i)
            kwargs = {"task_type": sub} if sub else {}
            task = gen(language="ru", difficulty=difficulty, **kwargs)
            fa = str(task.final_answer).strip()
            low = fa.lower()
            if low in ("да", "yes", "истина"):
                wrong = "нет"
            elif low in ("нет", "no", "ложь"):
                wrong = "да"
            elif re.fullmatch(r"-?\d+", fa):
                wrong = str(int(fa) + 7)
            elif "," in fa and all(x.strip().lstrip("-").isdigit() for x in fa.split(",")):
                wrong = ", ".join(str(int(x) + 1) for x in fa.split(","))
            else:
                wrong = "zzqqx"
            assert task.verify(f"<answer>{wrong}</answer>") < 1.0


# --- точечная корректность базовых алгоритмов ---

def test_lis_known():
    assert LISDPTask._lis([1, 3, 2, 4]) == 3
    assert LISDPTask._lis([5, 4, 3, 2, 1]) == 1
    assert LISDPTask._lis([1, 2, 3, 4, 5]) == 5
    assert LISDPTask._lis([3, 1, 2, 1, 5, 4]) == 3


def test_lps_known():
    assert LISDPTask._lps("bbabcbcab") == 7
    assert LISDPTask._lps("abcde") == 1
    assert LISDPTask._lps("aaaa") == 4
    assert LISDPTask._lps("agbdba") == 5  # abdba


def test_kmp_prefix_known():
    assert KMPMatchingTask._prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]
    assert KMPMatchingTask._prefix_function("abcabcd") == [0, 0, 0, 1, 2, 3, 0]
    assert KMPMatchingTask._prefix_function("aaaa") == [0, 1, 2, 3]


def test_kmp_count_overlapping():
    kmp = KMPMatchingTask.__new__(KMPMatchingTask)
    assert kmp._count_occurrences("aaaa", "aa") == 3
    assert kmp._count_occurrences("abababab", "abab") == 3
    assert kmp._count_occurrences("abcabc", "xyz") == 0


def test_sliding_solvable_rule():
    sp = SlidingPuzzleTask.__new__(SlidingPuzzleTask)
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    assert sp._is_solvable(goal, 3) is True
    # обмен двух соседних плиток делает 3x3 неразрешимой (1 инверсия — нечётно)
    swapped = (2, 1, 3, 4, 5, 6, 7, 8, 0)
    assert sp._is_solvable(swapped, 3) is False


def test_sliding_astar_optimal():
    sp = SlidingPuzzleTask.__new__(SlidingPuzzleTask)
    sp.n = 3
    goal = sp._goal()
    assert sp._astar(goal) == 0
    # один ход от цели: сдвигаем 8 (индекс 7) в пустую клетку (индекс 8)
    one = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    assert sp._astar(one) == 1


def test_resolution_one_step_manual():
    rt = ResolutionTask.__new__(ResolutionTask)
    rt.n_vars = 2
    rt.vars = ["A", "B"]
    c1 = frozenset([("A", True), ("B", True)])
    c2 = frozenset([("A", False), ("B", True)])
    # резольвента по A: {B} (нетавтологична) — одна штука
    res = rt._one_step_resolvents([c1, c2])
    assert frozenset([("B", True)]) in res
    assert len(res) == 1
    # комплементарная пара A и ¬A с общей B даёт (B ∨ ¬B) — тавтология, отбрасывается
    c3 = frozenset([("A", True)])
    c4 = frozenset([("A", False)])
    res2 = rt._one_step_resolvents([c3, c4])
    assert frozenset() in res2  # пустая клауза


def test_gale_shapley_known():
    from re_rl.tasks.math.logic.stable_matching_task import StableMatchingTask
    prefs_p = [[0, 1, 2], [1, 0, 2], [0, 1, 2]]
    prefs_a = [[1, 0, 2], [0, 1, 2], [0, 1, 2]]
    match, _ = StableMatchingTask.gale_shapley(prefs_p, prefs_a)
    assert match == [0, 1, 2]
    # m0—w2, m1—w1, m2—w0: пара (0, 0) блокирующая
    assert StableMatchingTask.blocking_pair([2, 1, 0], prefs_p, prefs_a) == (0, 0)
    assert StableMatchingTask.blocking_pair(match, prefs_p, prefs_a) is None


def test_hamming_syndrome_roundtrip():
    from re_rl.tasks.math.logic.hamming_code_task import HammingCodeTask
    for data_i in range(16):
        data = f"{data_i:04b}"
        code = HammingCodeTask.encode_data(data)
        assert HammingCodeTask.syndrome(code) == 0
        assert len(code) == 7
        for pos in range(1, 8):
            flipped = list(code)
            flipped[pos - 1] = "0" if flipped[pos - 1] == "1" else "1"
            assert HammingCodeTask.syndrome("".join(flipped)) == pos
    assert HammingCodeTask.hamming_distance("10110", "11100") == 2


def test_page_replacement_known():
    from re_rl.tasks.math.logic.page_replacement_task import PageReplacementTask
    refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    assert PageReplacementTask.simulate(refs, 3, "fifo")[0] == 9
    assert PageReplacementTask.simulate(refs, 3, "lru")[0] == 10
    assert PageReplacementTask.simulate([1, 2, 3, 2, 4], 2, "opt")[0] == 4
    # OPT не хуже FIFO и LRU
    fifo, _ = PageReplacementTask.simulate(refs, 3, "fifo")
    lru, _ = PageReplacementTask.simulate(refs, 3, "lru")
    opt, _ = PageReplacementTask.simulate(refs, 3, "opt")
    assert opt <= fifo and opt <= lru
    # один кадр: отказ на каждой смене страницы
    one = [1, 1, 2, 2, 1]
    assert PageReplacementTask.simulate(one, 1, "fifo")[0] == 3


def test_tree_queries_known():
    from re_rl.tasks.math.logic.tree_queries_task import TreeQueriesTask
    # рёбра 1-2, 2-3, 2-5, 3-4: диаметр 3 (4—5), листья 1,4,5, высота 3, LCA(4,5)=2
    adj = {1: [2], 2: [1, 3, 5], 3: [2, 4], 4: [3], 5: [2]}
    ends, dist = TreeQueriesTask.diameter(adj)
    assert dist == 3 and 4 in ends
    parents = {2: 1, 3: 2, 4: 3, 5: 2}
    assert TreeQueriesTask.lca(parents, 4, 5) == 2
    assert TreeQueriesTask.lca(parents, 4, 3) == 3
    assert TreeQueriesTask.lca(parents, 5, 1) == 1


def test_scheduling_and_numerical_known():
    from re_rl.tasks.math.logic.os_scheduling_task import OSSchedulingTask
    from re_rl.tasks.math.analysis.numerical_methods_task import NumericalMethodsTask
    from re_rl.tasks.math.discrete.min_coins_task import MinCoinsTask

    order, wait = OSSchedulingTask.sjf_waiting([4, 1, 3])
    assert order == [2, 3, 1] and wait == 5
    order, wait = OSSchedulingTask.fcfs_waiting([(0, 5), (1, 2), (2, 2)])
    assert order == [1, 2, 3] and wait == 9
    path, seek = OSSchedulingTask.sstf(50, [40, 60])
    assert path == [40, 60] and seek == 30

    assert NumericalMethodsTask.newton_step(2, 6) == 4
    ys, acc = NumericalMethodsTask.trapezoid(0, 3)
    assert ys == [0, 1, 4, 9] and acc == 19
    hist = NumericalMethodsTask.bisection_left(10, 16, 3)
    assert hist[-1][0] == 8

    opt, combo = MinCoinsTask.reconstruct(6, [1, 3, 4])
    assert opt == 2 and sorted(combo) == [3, 3]
    assert MinCoinsTask.greedy_count(6, [1, 3, 4]) == 3
