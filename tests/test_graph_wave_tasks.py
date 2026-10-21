"""Графовая волна: пути в DAG, число кратчайших путей, треугольники и обхват,
индекс Винера, радиус дерева, код Прюфера, Гавел–Хакими, остовные деревья
и число топологических порядков."""

import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.math.logic.dag_paths_task import count_paths
from re_rl.tasks.math.logic.shortest_count_task import bfs_ways
from re_rl.tasks.math.logic.triangle_girth_task import count_triangles, graph_girth
from re_rl.tasks.math.logic.wiener_task import wiener_index
from re_rl.tasks.math.logic.tree_radius_task import eccentricities
from re_rl.tasks.math.logic.prufer_task import prufer_encode
from re_rl.tasks.math.logic.havel_hakimi_task import is_graphic
from re_rl.tasks.math.logic.spanning_trees_task import spanning_trees
from re_rl.tasks.math.logic.topo_count_task import count_topological_orders

WAVE = [
    "dag_paths", "shortest_path_count", "triangle_girth", "wiener_index",
    "tree_radius", "prufer_code", "havel_hakimi", "spanning_trees", "topo_count",
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
        task = gen(task_type=sub, language="ru", difficulty=6)
        fa = str(task.final_answer).strip().lower()
        if fa in ("да", "yes"):
            wrong = "нет"
        elif fa in ("нет", "no"):
            wrong = "да"
        elif re.fullmatch(r"-?\d+", str(task.final_answer).strip()):
            wrong = str(int(task.final_answer) + 9)
        elif "," in str(task.final_answer):
            parts = [int(x) for x in str(task.final_answer).replace(" ", "").split(",")]
            wrong = ", ".join(str(x + 3) for x in parts)
        else:
            wrong = "zzqqx"
        assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_known_graph_answers():
    assert count_paths(3, [(1, 2), (2, 3), (1, 3)]) == 2
    dist, ways = bfs_ways(4, [[], [2, 3], [1, 4], [1, 4], [2, 3]], 1)
    assert dist[4] == 2 and ways[4] == 2
    triangle = [(1, 2), (2, 3), (1, 3)]
    assert count_triangles(3, triangle) == 1
    assert graph_girth(3, triangle) == 3
    assert graph_girth(3, [(1, 2), (2, 3)]) == 0
    assert wiener_index(3, [(1, 2), (2, 3)]) == 4
    ecc = eccentricities(4, [(1, 2), (2, 3), (3, 4)])
    assert min(ecc[1:]) == 2 and ecc[1] == 3
    assert prufer_encode(4, [(1, 2), (2, 3), (3, 4)]) == [2, 3]
    assert is_graphic([2, 2, 2]) is True
    assert is_graphic([1, 1, 1]) is False
    assert is_graphic([3, 1, 1, 1]) is True
    assert spanning_trees(3, [(0, 1), (1, 2)]) == 1
    assert spanning_trees(3, [(0, 1), (1, 2), (0, 2)]) == 3
    assert spanning_trees(3, []) == 0
    assert count_topological_orders(3, []) == 6
    assert count_topological_orders(3, [(0, 1)]) == 3
    assert count_topological_orders(3, [(0, 1), (1, 2)]) == 1
