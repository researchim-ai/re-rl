"""Формальная логика: классификация формул, подсчёт моделей, 3-SAT,
эквивалентность формул, квантифицированные булевы формулы (мини-QBF)."""

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_VARS = ["p", "q", "r", "s", "t"]


def _rand_formula(vars: List[str], depth: int, max_depth: int):
    if depth <= 0 or (depth < max_depth and random.random() < 0.35):
        return ("var", random.choice(vars))
    op = random.choice(["not", "and", "or", "imp", "iff"])
    if op == "not":
        return ("not", _rand_formula(vars, depth - 1, max_depth))
    return (op, _rand_formula(vars, depth - 1, max_depth),
            _rand_formula(vars, depth - 1, max_depth))


def _eval(node, assign):
    t = node[0]
    if t == "var":
        return assign[node[1]]
    if t == "not":
        return not _eval(node[1], assign)
    a = _eval(node[1], assign)
    b = _eval(node[2], assign)
    if t == "and":
        return a and b
    if t == "or":
        return a or b
    if t == "imp":
        return (not a) or b
    return a == b


def _render(node):
    t = node[0]
    if t == "var":
        return node[1]
    if t == "not":
        return f"¬{_render(node[1])}"
    sym = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[t]
    return f"({_render(node[1])} {sym} {_render(node[2])})"


class _LogicBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task















