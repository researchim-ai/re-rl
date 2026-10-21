"""База машинного обучения: энтропия, Джини, kNN, перцептрон, k-means,
наивный Байес, матрица ошибок, шаг градиента и AUC.

Ответы-дроби сравниваются точно.
"""

import random
import re

import pytest
from fractions import Fraction

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from re_rl.tasks.ml.entropy_task import shannon_bits
from re_rl.tasks.ml.gini_task import gini, gini_gain
from re_rl.tasks.ml.knn_task import neighbors
from re_rl.tasks.ml.perceptron_task import perceptron_step
from re_rl.tasks.ml.kmeans_task import assign_to_first
from re_rl.tasks.ml.naive_bayes_task import score
from re_rl.tasks.ml.confusion_task import counts
from re_rl.tasks.ml.gradient_step_task import gradient
from re_rl.tasks.ml.ranking_auc_task import concordant_pairs

ML_TYPES = [
    "shannon_entropy", "gini_split", "knn_classify", "perceptron_update",
    "kmeans_step", "naive_bayes", "confusion_metrics", "gradient_step", "ranking_auc",
]


def _seed(*parts):
    random.seed("|".join(map(str, parts)))


@pytest.mark.parametrize("task_type", ML_TYPES)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", ML_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(3):
            _seed(task_type, sub, language, difficulty, i)
            task = gen(task_type=sub, language=language, difficulty=difficulty)
            assert task.final_answer is not None
            assert "{" not in task.description and "}" not in task.description
            assert task.solution_steps
            assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0


@pytest.mark.parametrize("task_type", ML_TYPES)
def test_wrong_answer_rejected(task_type):
    gen = ALL_TASK_GENERATORS[task_type]
    cls = registry[task_type]
    for sub in getattr(cls, "TASK_TYPES", [None]):
        for i in range(3):
            _seed("bad", task_type, sub, i)
            task = gen(task_type=sub, language="ru", difficulty=6)
            fa = str(task.final_answer).strip()
            if fa in ("A", "B"):
                wrong = "B" if fa == "A" else "A"
            elif re.fullmatch(r"-?\d+", fa):
                wrong = str(int(fa) + 9)
            elif "," in fa:
                parts = [int(x) for x in fa.replace(" ", "").split(",") if x]
                wrong = ", ".join(str(x + 3) for x in parts)
            else:
                wrong = "zzqqx"
            assert task.verify(f"<answer>{wrong}</answer>") < 1.0


def test_shannon_known():
    assert shannon_bits([8]) == 0
    assert shannon_bits([4, 4]) == 1
    assert shannon_bits([4, 2, 2]) == Fraction(3, 2)


def test_gini_known():
    assert gini([3, 3]) == Fraction(1, 2)
    rows = [(0, 0, 0), (0, 0, 0), (1, 1, 0), (1, 1, 0)]
    # fA идеально отделяет классы, fB постоянен
    assert gini_gain(rows, 1) == Fraction(1, 2)
    assert gini_gain(rows, 2) == 0


def test_knn_known():
    train = [(0, 0, "A"), (5, 0, "B"), (0, 4, "B")]
    assert neighbors(train, (1, 0), 1) == [0]
    voted = neighbors(train, (1, 0), 1)
    assert train[voted[0]][2] == "A"


def test_perceptron_known():
    w, b, updated = perceptron_step([0, 0], 0, (1, 0, 1))
    assert updated and w == [1, 0] and b == 1
    w2, b2, updated2 = perceptron_step(w, b, (1, 0, 1))
    assert updated2 is False and w2 == [1, 0] and b2 == 1


def test_kmeans_tie_goes_to_first():
    assert assign_to_first((0, 0), (1, 0), (-1, 0)) is True
    assert assign_to_first((5, 0), (0, 0), (10, 0)) is True
    assert assign_to_first((8, 0), (0, 0), (10, 0)) is False


def test_naive_bayes_prefers_matching_class():
    rows = [(1, 1, "A")] * 4 + [(0, 0, "B")] * 4
    assert score(rows, "A", (1, 1)) > score(rows, "B", (1, 1))


def test_confusion_known():
    c = counts([1, 1, 0, 0], [1, 0, 1, 0])
    assert c == {"tp": 1, "fp": 1, "fn": 1, "tn": 1}
    assert Fraction(c["tp"], c["tp"] + c["fp"]) == Fraction(1, 2)
    assert Fraction(2 * c["tp"], 2 * c["tp"] + c["fp"] + c["fn"]) == Fraction(1, 2)


def test_gradient_known():
    # w = 0, точки (1, 1), (2, 2): g = -1 - 4 = -5, новый вес 5
    assert gradient(0, [(1, 1), (2, 2)]) == -5


def test_auc_known():
    # положительные оценки 1 и 2, отрицательные 3 и 0: согласованы две пары из четырёх
    items = [(1, 1), (0, 3), (1, 2), (0, 0)]
    assert concordant_pairs(items) == 2
    assert Fraction(2, 4) == Fraction(1, 2)
    assert concordant_pairs([(1, 3), (0, 1), (1, 2), (0, 0)]) == 4
