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
