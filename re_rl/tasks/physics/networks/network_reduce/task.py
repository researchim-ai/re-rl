"""NetworkReduceTask — целое эквивалентное сопротивление дерева.

Последовательное соединение складывает сопротивления. Параллельное здесь всегда из двух равных ветвей, поэтому результат — половина, и она целая.
Число листьев растёт с уровнем, эквивалент считается снизу вверх.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Tuple, Union

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Leaf = Tuple[str, int]
Node = Union[Leaf, Tuple[str, "Node", "Node"]]
Shape = Union[Tuple[str], Tuple[str, "Shape", "Shape"]]


def make_shape(leaves: int) -> Shape:
    if leaves == 1:
        return ("leaf",)
    cut = random.randint(1, leaves - 1)
    kind = "series" if random.random() < 0.5 else "parallel"
    return (kind, make_shape(cut), make_shape(leaves - cut))


def assign(shape: Shape, value: int) -> Node:
    if shape[0] == "leaf":
        return ("leaf", value)
    left_leaves = _shape_leaves(shape[1])
    right_leaves = _shape_leaves(shape[2])
    if shape[0] == "series":
        left_value = random.randint(left_leaves, value - right_leaves)
        return (
            "series",
            assign(shape[1], left_value),
            assign(shape[2], value - left_value),
        )
    doubled = value * 2
    return ("parallel", assign(shape[1], doubled), assign(shape[2], doubled))


def _shape_leaves(shape: Shape) -> int:
    if shape[0] == "leaf":
        return 1
    return _shape_leaves(shape[1]) + _shape_leaves(shape[2])


def equivalent(node: Node) -> int:
    if node[0] == "leaf":
        return node[1]
    left = equivalent(node[1])
    right = equivalent(node[2])
    if node[0] == "series":
        return left + right
    return left * right // (left + right)


def leaf_sum(node: Node) -> int:
    if node[0] == "leaf":
        return node[1]
    return leaf_sum(node[1]) + leaf_sum(node[2])


class NetworkReduceTask(BaseMathTask):
    TASK_TYPE = "network_reduce"
    TASK_TYPES = ["equivalent", "leaf_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "e": 2}, 2: {"n": 2, "e": 3}, 3: {"n": 3, "e": 3},
        4: {"n": 3, "e": 4}, 5: {"n": 4, "e": 4}, 6: {"n": 5, "e": 4},
        7: {"n": 6, "e": 5}, 8: {"n": 7, "e": 5}, 9: {"n": 8, "e": 6},
        10: {"n": 10, "e": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        root = self.n + random.randint(0, int(p["e"]))
        self.tree = assign(make_shape(self.n), root)
        self.equivalent = equivalent(self.tree)
        self.total_leaves = leaf_sum(self.tree)
        self.answer = self.equivalent if self.task_type == "equivalent" else self.total_leaves
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _render(self, node: Node, language: str) -> str:
        if node[0] == "leaf":
            return texts.t("s2", language, r=node[1])
        key = "s3" if node[0] == "series" else "s4"
        return texts.t(key, language, left=self._render(node[1], language), right=self._render(node[2], language))

    def _descr(self, language):
        key = "s0" if self.task_type == "equivalent" else "s1"
        return texts.t(key, language, n=self.n, expr=self._render(self.tree, language))

    def _reduce(self, node: Node, steps: list) -> int:
        if node[0] == "leaf":
            return node[1]
        left = self._reduce(node[1], steps)
        right = self._reduce(node[2], steps)
        if node[0] == "series":
            value = left + right
            steps.append(texts.t("s5", self.language, left=left, right=right, value=value))
        else:
            value = left * right // (left + right)
            steps.append(texts.t("s6", self.language, left=left, right=right, value=value))
        return value

    def solve(self):
        steps = []
        self._reduce(self.tree, steps)
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
