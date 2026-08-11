"""InequalityProofTask — верно ли, что квадратичное выражение неотрицательно ∀x.

Даётся выражение a·x² + b·x + c; нужно определить, выполнено ли ``≥ 0`` для всех
действительных x. Задача полностью решаема аналитически (знак старшего
коэффициента и дискриминант), поэтому эталон однозначен. Ответ YES/NO.
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class InequalityProofTask(BaseMathTask):
    """Неотрицательность квадратного трёхчлена при всех x (YES/NO)."""

    TASK_TYPE = "inequality_proof"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_coeff": 3},
        2: {"max_coeff": 4},
        3: {"max_coeff": 5},
        4: {"max_coeff": 6},
        5: {"max_coeff": 7},
        6: {"max_coeff": 8},
        7: {"max_coeff": 10},
        8: {"max_coeff": 12},
        9: {"max_coeff": 15},
        10: {"max_coeff": 20},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        max_coeff: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.max_coeff = int(max_coeff if max_coeff is not None else preset.get("max_coeff", 7))
        self.augment = augment

        self.x = sp.Symbol("x")
        self.a, self.b, self.c = self._make_coeffs()
        self._always_nonneg = self._decide()

        expr = self.a * self.x ** 2 + self.b * self.x + self.c
        expr_str = sp.sstr(sp.expand(expr)).replace("**", "^")
        description = get_template(
            PROMPT_TEMPLATES["inequality_proof"], "problem", language,
            augment=augment, expr=expr_str,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_coeffs(self):
        # ~50% случаев конструируем заведомо неотрицательный (a>0, D<=0).
        if random.random() < 0.5:
            a = random.randint(1, self.max_coeff)
            # Полный квадрат плюс неотрицательная добавка: (px+q)^2 + r, r>=0.
            p = random.randint(1, max(1, int(self.max_coeff ** 0.5)))
            q = random.randint(-self.max_coeff, self.max_coeff)
            r = random.randint(0, self.max_coeff)
            a = p * p
            b = 2 * p * q
            c = q * q + r
            return a, b, c
        # Иначе случайные коэффициенты (часто НЕ всегда неотрицательно).
        a = random.choice([-1, 1]) * random.randint(1, self.max_coeff)
        b = random.randint(-self.max_coeff, self.max_coeff)
        c = random.randint(-self.max_coeff, self.max_coeff)
        return a, b, c

    def _decide(self) -> bool:
        # a x^2 + b x + c >= 0 для всех x  <=>  (a>0 и D<=0) или (a==0,b==0,c>=0)
        a, b, c = self.a, self.b, self.c
        if a == 0:
            return b == 0 and c >= 0
        disc = b * b - 4 * a * c
        return a > 0 and disc <= 0

    def solve(self):
        section = PROMPT_TEMPLATES["inequality_proof"]
        answer = "YES" if self._always_nonneg else "NO"
        self.solution_steps.append(get_template(section, "step_discriminant", self.language, augment=False))
        verdict = ("выполнено" if self._always_nonneg else "не выполнено") if self.language == "ru" \
            else ("holds" if self._always_nonneg else "does not hold")
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, verdict=verdict, answer=answer)
        )
        self.final_answer = answer

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip().lower().strip(".!? ")
        if text in {"yes", "да", "true", "y", "1", "верно"}:
            pred = "YES"
        elif text in {"no", "нет", "false", "n", "0", "неверно"}:
            pred = "NO"
        elif re.search(r"\b(no|нет|false|неверно)\b", text):
            pred = "NO"
        elif re.search(r"\b(yes|да|true|верно)\b", text):
            pred = "YES"
        else:
            return 0.0
        return 1.0 if pred == self.final_answer else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "InequalityProofTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
