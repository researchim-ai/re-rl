"""Общие утилиты верификации для логических/ризонинг-задач.

Содержит парсеры ответа модели (да/нет, целые числа, последовательности,
метки-синонимы) и безопасный вычислитель арифметических выражений.
"""

from __future__ import annotations

import ast
import operator
import re
from typing import List, Optional

from re_rl.tasks.math._verify_utils import extract_answer_text

_YES = {"yes", "да", "true", "верно", "истина", "истинно"}
_NO = {"no", "нет", "false", "неверно", "ложь", "ложно"}


def clean(prediction: str) -> str:
    """Возвращает текст ответа (из ``<answer>`` при наличии) в нижнем регистре."""
    return extract_answer_text(prediction).strip()


def _words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())


def parse_bool(prediction: str) -> Optional[bool]:
    """Определяет булев ответ по последнему встреченному да/нет-слову."""
    last_val: Optional[bool] = None
    for w in _words(prediction):
        if w in _YES:
            last_val = True
        elif w in _NO:
            last_val = False
    return last_val


def verify_bool(prediction: str, truth: bool) -> float:
    val = parse_bool(prediction)
    if val is None:
        return 0.0
    return 1.0 if val == truth else 0.0


def parse_ints(prediction: str) -> List[int]:
    """Все целые числа из ответа (с поддержкой юникод-минуса)."""
    txt = extract_answer_text(prediction).replace("−", "-").replace("—", "-")
    return [int(x) for x in re.findall(r"-?\d+", txt)]


def last_int(prediction: str) -> Optional[int]:
    ints = parse_ints(prediction)
    return ints[-1] if ints else None


def verify_int(prediction: str, truth: int, use_last: bool = True) -> float:
    ints = parse_ints(prediction)
    if not ints:
        return 0.0
    cand = ints[-1] if use_last else ints[0]
    return 1.0 if cand == truth else 0.0


def verify_int_sequence(prediction: str, truth: List[int]) -> float:
    """Совпадение последних ``len(truth)`` чисел ответа с эталонной последовательностью."""
    ints = parse_ints(prediction)
    if len(ints) < len(truth):
        return 0.0
    return 1.0 if ints[-len(truth):] == list(truth) else 0.0


def normalize(text: str) -> str:
    """Нижний регистр, схлопнутые пробелы, без знаков препинания."""
    text = extract_answer_text(text).lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def verify_label(prediction: str, synonyms: List[str]) -> float:
    """1.0, если в нормализованном ответе встречается любой из синонимов."""
    norm = " " + normalize(prediction) + " "
    for syn in synonyms:
        s = normalize(syn)
        if s and (" " + s + " ") in norm:
            return 1.0
    return 0.0


def _find_run(tokens: List[str], sub: List[str]) -> int:
    """Индекс первого вхождения подпоследовательности токенов ``sub`` (или -1)."""
    if not sub:
        return -1
    for i in range(len(tokens) - len(sub) + 1):
        if tokens[i:i + len(sub)] == sub:
            return i
    return -1


def extract_name_sequence(prediction: str, names: List[str]) -> List[str]:
    """Возвращает имена в порядке появления, сопоставляя их как целые слова.

    Пословное сравнение (а не поиск подстроки) исключает ложные совпадения вида
    «Анна» ⊂ «Жанна».
    """
    tokens = normalize(prediction).split()
    positions = []
    for name in names:
        idx = _find_run(tokens, normalize(name).split())
        if idx >= 0:
            positions.append((idx, name))
    positions.sort()
    return [name for _, name in positions]


# --- Безопасный арифметический вычислитель (для countdown_24 и пр.) ---

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(expr: str) -> Optional[float]:
    """Безопасно вычисляет арифметическое выражение (+ - * / и скобки).

    Возвращает ``None`` при синтаксической ошибке, делении на ноль или
    недопустимых конструкциях.
    """
    expr = expr.replace("×", "*").replace("·", "*").replace("÷", "/")
    expr = expr.replace("−", "-").replace("—", "-").replace("^", "**")
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError:
        return None

    def _ev(n):
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_BINOPS:
            a, b = _ev(n.left), _ev(n.right)
            if a is None or b is None:
                return None
            if isinstance(n.op, ast.Div) and abs(b) < 1e-12:
                return None
            return _ALLOWED_BINOPS[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            v = _ev(n.operand)
            return None if v is None else (v if isinstance(n.op, ast.UAdd) else -v)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        return None

    return _ev(node)


def numbers_in_expr(expr: str) -> List[int]:
    """Целые числа-операнды в выражении (для проверки использования чисел)."""
    expr = expr.replace("×", "*").replace("·", "*").replace("÷", "/").replace("−", "-")
    return [int(x) for x in re.findall(r"\d+", expr)]


# --- Латинские квадраты (для «Небоскрёбов» и KenKen) ---

from itertools import permutations as _perms  # noqa: E402

_LATIN_CACHE: dict = {}


def all_latin_squares(n: int) -> List[tuple]:
    """Все латинские квадраты порядка ``n`` как кортежи строк-кортежей.

    Значения 1..n; каждая строка и столбец — перестановка. Результат кэшируется.
    Практично для n ≤ 4 (n=4 → 576 квадратов).
    """
    if n in _LATIN_CACHE:
        return _LATIN_CACHE[n]
    rows_all = list(_perms(range(1, n + 1)))
    result: List[tuple] = []

    def ok(grid, cand):
        r = len(grid)
        for c in range(n):
            col = [grid[i][c] for i in range(r)]
            if cand[c] in col:
                return False
        return True

    def bt(grid):
        if len(grid) == n:
            result.append(tuple(grid))
            return
        for cand in rows_all:
            if ok(grid, cand):
                grid.append(cand)
                bt(grid)
                grid.pop()

    bt([])
    _LATIN_CACHE[n] = result
    return result
