"""Общие утилиты для семантической верификации ответов математических задач.

Содержит хелперы для извлечения ответа из ``<answer>``-тегов и символической
проверки эквивалентности через sympy. Импорт из :mod:`re_rl.rewards` делается
лениво, чтобы избежать циклических зависимостей.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

import sympy as sp


def extract_answer_text(prediction: str) -> str:
    """Достаёт текст ответа из ``<answer>`` (если есть) либо возвращает как есть."""
    from re_rl.rewards import extract_reasoning_and_answer

    _, answer = extract_reasoning_and_answer(prediction)
    return (answer or prediction).strip()


def clean_expr_text(text: str) -> str:
    """Нормализует строку выражения перед sympify."""
    text = text.strip().rstrip(".").strip()
    # Берём правую часть, если ответ вида "f(x) = ..." или "y = ...".
    if "=" in text:
        text = text.split("=")[-1].strip()
    text = text.replace("^", "**")
    return text


def parse_expr(text: str, symbols: Iterable, local_syms: Optional[dict] = None) -> Optional[sp.Expr]:
    """Пробует распарсить выражение с заданными символами.

    ``symbols`` — имена переменных (строки) либо готовые ``sympy.Symbol``.
    ``local_syms`` при наличии задаёт точное соответствие имя→Symbol (важно,
    когда у эталонного символа заданы предположения вроде ``integer=True``).
    """
    if local_syms is None:
        loc = {}
        for s in symbols:
            if isinstance(s, sp.Symbol):
                loc[s.name] = s
            else:
                loc[str(s)] = sp.Symbol(str(s))
    else:
        loc = local_syms
    try:
        return sp.sympify(clean_expr_text(text), locals=loc)
    except (sp.SympifyError, SyntaxError, TypeError, ValueError, AttributeError):
        return None


def sympy_equiv(prediction: str, ref_expr: sp.Expr, symbols: Iterable,
                local_syms: Optional[dict] = None) -> float:
    """1.0, если распарсенный ответ символически равен ``ref_expr``."""
    expr = parse_expr(extract_answer_text(prediction), symbols, local_syms=local_syms)
    if expr is None:
        return 0.0
    try:
        return 1.0 if sp.simplify(expr - ref_expr) == 0 else 0.0
    except Exception:
        return 0.0


def extract_numbers(text: str) -> List[float]:
    """Извлекает все числа (в т.ч. дроби a/b) из текста как float."""
    text = text.replace("−", "-")
    result: List[float] = []
    # Сначала дроби вида a/b.
    tokens = re.findall(r"[-+]?\d+\s*/\s*\d+|[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    for tok in tokens:
        tok = tok.replace(" ", "")
        try:
            if "/" in tok:
                num, den = tok.split("/")
                result.append(float(num) / float(den))
            else:
                result.append(float(tok))
        except (ValueError, ZeroDivisionError):
            continue
    return result


def numbers_match(pred_nums: List[float], ref_nums: List[float], tol: float = 1e-6) -> bool:
    """Совпадают ли два набора чисел (по порядку) с точностью tol."""
    if len(pred_nums) != len(ref_nums):
        return False
    return all(abs(a - b) <= tol * max(1.0, abs(b)) + tol for a, b in zip(pred_nums, ref_nums))
