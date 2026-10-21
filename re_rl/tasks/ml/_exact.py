"""Точные дроби для задач машинного обучения.

Ответы сравниваются как ``fractions.Fraction``, а не как float: ``3/2`` и ``1.5``
совпадают, ``0.33`` не считается равным ``1/3``.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

from re_rl.tasks.math._verify_utils import extract_answer_text


def fmt_fraction(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(prediction: str) -> Optional[Fraction]:
    """Последняя дробь ``a/b`` либо последнее число (в том числе десятичное)."""
    txt = extract_answer_text(prediction).replace("−", "-").replace("—", "-").replace(",", ".")
    fracs = list(re.finditer(r"(-?\d+)\s*/\s*(-?\d+)", txt))
    if fracs:
        num, den = int(fracs[-1].group(1)), int(fracs[-1].group(2))
        if den == 0:
            return None
        return Fraction(num, den)
    nums = re.findall(r"-?\d+(?:\.\d+)?", txt)
    if not nums:
        return None
    token = nums[-1]
    if "." in token:
        return Fraction(token)
    return Fraction(int(token), 1)


def verify_fraction(prediction: str, truth: Fraction) -> float:
    got = parse_fraction(prediction)
    if got is None:
        return 0.0
    return 1.0 if got == Fraction(truth) else 0.0
