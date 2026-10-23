"""SwitchNetTask — проводимость дерева выключателей.

Последовательное соединение проводит, только если проводят обе ветви.
Параллельное проводит, если проводит хотя бы одна.
Число выключателей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple, Union

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Leaf = Tuple[str, int, int]
Node = Union[Leaf, Tuple[str, "Node", "Node"]]
Shape = Union[Tuple[str], Tuple[str, "Shape", "Shape"]]


def make_shape(leaves: int) -> Shape:
    if leaves == 1:
        return ("leaf",)
    cut = random.randint(1, leaves - 1)
    kind = "series" if random.random() < 0.5 else "parallel"
    return (kind, make_shape(cut), make_shape(leaves - cut))


def label_tree(shape: Shape, nxt: List[int]) -> Node:
    if shape[0] == "leaf":
        nxt[0] += 1
        return ("leaf", nxt[0], random.randint(0, 1))
    return (shape[0], label_tree(shape[1], nxt), label_tree(shape[2], nxt))


def evaluate(node: Node) -> int:
    if node[0] == "leaf":
        return node[2]
    left = evaluate(node[1])
    right = evaluate(node[2])
    if node[0] == "series":
        return left & right
    return left | right


def flip_leaf(node: Node, switch: int) -> Node:
    if node[0] == "leaf":
        if node[1] == switch:
            return ("leaf", node[1], 1 - node[2])
        return node
    return (node[0], flip_leaf(node[1], switch), flip_leaf(node[2], switch))


def render_tree(node: Node) -> str:
    if node[0] == "leaf":
        return f"{node[1]}:{node[2]}"
    op = "&" if node[0] == "series" else "|"
    return f"({render_tree(node[1])} {op} {render_tree(node[2])})"


class SwitchNetTask(BaseMathTask):
    TASK_TYPE = "switch_net"
    TASK_TYPES = ["conducts", "flip"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.tree = label_tree(make_shape(self.n), [0])
        self.conducts = evaluate(self.tree)
        self.k = random.randint(1, self.n)
        self.flipped = flip_leaf(self.tree, self.k)
        self.flipped_value = evaluate(self.flipped)
        self.changes = int(self.flipped_value != self.conducts)
        self.answer = self.conducts if self.task_type == "conducts" else self.changes
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "conducts" else "s1"
        return texts.t(key, language, n=self.n, expr=render_tree(self.tree), k=self.k)

    def _trace(self, node: Node, steps: list) -> int:
        if node[0] == "leaf":
            return node[2]
        left = self._trace(node[1], steps)
        right = self._trace(node[2], steps)
        if node[0] == "series":
            value = left & right
            steps.append(texts.t("s2", self.language, left=left, right=right, value=value))
        else:
            value = left | right
            steps.append(texts.t("s3", self.language, left=left, right=right, value=value))
        return value

    def solve(self):
        steps = []
        self._trace(self.tree, steps)
        if self.task_type == "flip":
            self._trace(self.flipped, steps)
            steps.append(texts.t(
                "s4", self.language, k=self.k, before=self.conducts,
                after=self.flipped_value, changes=self.changes,
            ))
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
