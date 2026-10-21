"""В Python-коде пакета не остаётся пользовательских фраз."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "re_rl"
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
PROSE_FILES = {"task.py", "dataset_generator.py", "multiturn_generator.py", "factory.py"}


def _docstring_ids(tree: ast.AST) -> set[int]:
    ids: set[int] = set()

    def mark(body):
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ids.add(id(body[0].value))

    mark(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            mark(node.body)
    return ids


def _string_pieces(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        return [
            "".join(
                part.value
                for part in node.values
                if isinstance(part, ast.Constant) and isinstance(part.value, str)
            )
        ]
    return []


def _is_language_compare(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare):
        return False
    for op, comparator in zip(node.ops, node.comparators):
        if not isinstance(op, (ast.Eq, ast.NotEq)):
            continue
        if not isinstance(comparator, ast.Constant) or comparator.value not in {"ru", "en"}:
            continue
        left = ast.unparse(node.left)
        if "language" in left or left in {"lang", "ru"}:
            return True
    return False


def test_no_cyrillic_or_language_switch_in_python():
    cyrillic = []
    switches = []
    prose = []
    for path in ROOT.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        documented = _docstring_ids(tree)
        relative = path.relative_to(ROOT)
        for node in ast.walk(tree):
            if _is_language_compare(node):
                switches.append(f"{relative}:{node.lineno}")
            if isinstance(node, ast.Constant) and id(node) in documented:
                continue
            for text in _string_pieces(node):
                if CYRILLIC.search(text):
                    cyrillic.append(f"{relative}:{getattr(node, 'lineno', 0)}: {text[:60]}")
                if (
                    path.name in PROSE_FILES
                    and " " in text
                    and len(LATIN_WORD.findall(text)) >= 3
                ):
                    prose.append(f"{relative}:{getattr(node, 'lineno', 0)}: {text[:60]}")
    assert cyrillic == []
    assert switches == []
    assert prose == []
