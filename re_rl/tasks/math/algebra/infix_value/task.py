"""InfixValueTask — значение выражения с плюсом, умножением и скобками.

Умножение выполняется раньше сложения. Скобки меняют порядок.
Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple, Union

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Tree = Union[Tuple[str, int], Tuple[str, "Tree", "Tree"]]


def gen_tree(ops: int) -> Tree:
    if ops == 0:
        return ("num", random.randint(1, 9))
    left_ops = random.randint(0, ops - 1)
    op = random.choice(("+", "*"))
    return (op, gen_tree(left_ops), gen_tree(ops - 1 - left_ops))


def render_tree(tree: Tree, parent: str = "") -> str:
    if tree[0] == "num":
        return str(tree[1])
    op, left, right = tree
    body = render_tree(left, op) + " " + op + " " + render_tree(right, op)
    if parent == "*" and op == "+":
        return "(" + body + ")"
    return body


def eval_tree(tree: Tree) -> Tuple[int, int]:
    if tree[0] == "num":
        return tree[1], 0
    op, left, right = tree
    left_value, left_muls = eval_tree(left)
    right_value, right_muls = eval_tree(right)
    if op == "+":
        return left_value + right_value, left_muls + right_muls
    return left_value * right_value, left_muls + right_muls + 1


def eval_infix(expr: str) -> Tuple[int, int, List[Tuple[str, int, int]]]:
    tokens = expr.replace("(", " ( ").replace(")", " ) ").split()
    index = 0
    steps: List[Tuple[str, int, int]] = []
    muls = 0

    def peek() -> str:
        return tokens[index] if index < len(tokens) else ""

    def factor() -> int:
        nonlocal index
        if peek() == "(":
            index += 1
            value = expression()
            index += 1
            return value
        index += 1
        return int(tokens[index - 1])

    def term() -> int:
        nonlocal index, muls
        value = factor()
        while peek() == "*":
            index += 1
            right = factor()
            value *= right
            muls += 1
            steps.append(("*", value, muls))
        return value

    def expression() -> int:
        nonlocal index
        value = term()
        while peek() == "+":
            index += 1
            right = term()
            value += right
            steps.append(("+", value, muls))
        return value

    value = expression()
    return value, muls, steps


class InfixValueTask(BaseMathTask):
    TASK_TYPE = "infix_value"
    TASK_TYPES = ["value", "muls"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.tree = gen_tree(self.n)
        self.expr = render_tree(self.tree)
        tree_value, tree_muls = eval_tree(self.tree)
        self.value, self.muls, self.trace = eval_infix(self.expr)
        assert self.value == tree_value and self.muls == tree_muls and len(self.trace) == self.n
        self.answer = self.value if self.task_type == "value" else self.muls
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, expr=self.expr)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=op, value=value, muls=muls)
            for index, (op, value, muls) in enumerate(self.trace, 1)
        ]
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
