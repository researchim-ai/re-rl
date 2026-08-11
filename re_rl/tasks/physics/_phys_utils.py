"""Общие утилиты для новых физических задач.

- ``fmt`` — единообразное форматирование числовых значений;
- ``NumericPhysicsVerifyMixin`` — числовая проверка ответа с относительным
  допуском (сравнивает последние N чисел ответа с эталонными).
"""

from __future__ import annotations

import re
from typing import List

from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers

# Метка величины перед знаком равенства, например «R1 =», «I₃ =», «λ_max =».
# Такие подписи вырезаются, чтобы их цифровые индексы не попадали в числа ответа.
_LABEL_RE = re.compile(r"[A-Za-zА-Яа-яα-ωΑ-Ω_][\w₀-₉]*\s*=")


def fmt(value: float, precision: int = 6) -> str:
    """Форматирует число с ``precision`` значащими цифрами.

    Для очень малых/больших значений используется научная запись. Используются
    значащие цифры (``g``), а не фиксированные знаки после запятой, чтобы не
    терять точность на величинах порядка ``1e-3``.
    """
    if value == 0:
        return "0"
    if abs(value) < 1e-3 or abs(value) >= 1e6:
        return f"{value:.3e}"
    return f"{value:.{precision}g}"


def _close(a: float, b: float, rtol: float = 0.02, atol: float = 1e-9) -> bool:
    return abs(a - b) <= atol + rtol * max(abs(a), abs(b))


class NumericPhysicsVerifyMixin:
    """Проверяет ответ по эталонным числам ``self._answer_numbers``.

    Сравниваются последние ``len(ref)`` чисел из ответа модели с эталоном
    (относительный допуск 2%). Если эталонные числа не заданы, делегирует
    базовой логике сравнения из :mod:`re_rl.rewards`.
    """

    _answer_numbers: List[float]

    def verify(self, prediction: str) -> float:  # type: ignore[override]
        if getattr(self, "final_answer", None) is None:
            self.solve()
        ref = getattr(self, "_answer_numbers", None)
        if not ref:
            from re_rl.rewards import compute_correctness_score
            return compute_correctness_score(self.TASK_TYPE, str(self.final_answer), prediction)
        cleaned = _LABEL_RE.sub(" ", extract_answer_text(prediction))
        nums = extract_numbers(cleaned)
        if len(nums) < len(ref):
            return 0.0
        cand = nums[-len(ref):]
        return 1.0 if all(_close(a, b) for a, b in zip(cand, ref)) else 0.0
