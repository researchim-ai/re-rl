"""SymbolicRegressionTask — восстановить формулу f(x) по таблице значений.

Скрытая функция — многочлен с целыми коэффициентами. В условии даётся набор
точек (x, f(x)), достаточный для однозначного определения. Проверка ответа
выполняется подстановкой в точки (в т.ч. новые), что эквивалентно проверке
совпадения функций на всей области.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class SymbolicRegressionTask(BaseMathTask):
    """Угадать многочлен f(x) по таблице значений."""

    TASK_TYPE = "symbolic_regression"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 1, "max_coeff": 3},
        2: {"degree": 1, "max_coeff": 5},
        3: {"degree": 2, "max_coeff": 3},
        4: {"degree": 2, "max_coeff": 5},
        5: {"degree": 2, "max_coeff": 6},
        6: {"degree": 3, "max_coeff": 4},
        7: {"degree": 3, "max_coeff": 5},
        8: {"degree": 3, "max_coeff": 6},
        9: {"degree": 4, "max_coeff": 4},
        10: {"degree": 4, "max_coeff": 5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        degree: Optional[int] = None,
        max_coeff: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.degree = int(degree if degree is not None else preset.get("degree", 2))
        self.max_coeff = int(max_coeff if max_coeff is not None else preset.get("max_coeff", 5))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._poly = self._make_polynomial()
        # Точек чуть больше степени для однозначности.
        self._xs = list(range(-(self.degree // 2) - 1, self.degree + 3))
        self._points = [(xv, int(self._poly.subs(self.x, xv))) for xv in self._xs]

        table = "\n".join(f"  x = {xv}: f(x) = {fv}" for xv, fv in self._points)
        description = get_template(
            PROMPT_TEMPLATES["symbolic_regression"], "problem", language,
            augment=augment, table=table,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_polynomial(self) -> sp.Expr:
        while True:
            coeffs = [random.randint(-self.max_coeff, self.max_coeff) for _ in range(self.degree + 1)]
            if coeffs[0] == 0:
                coeffs[0] = random.choice([-1, 1]) * random.randint(1, self.max_coeff)
            expr = sum(c * self.x ** (self.degree - i) for i, c in enumerate(coeffs))
            expr = sp.expand(expr)
            # Требуем, чтобы функция реально зависела от x.
            if expr.has(self.x):
                return expr

    def _format_expr(self, expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["symbolic_regression"]
        result = self._format_expr(self._poly)
        self.solution_steps.append(get_template(section, "step_fit", self.language, augment=False))
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        """Совпадение с искомой функцией на точках таблицы и нескольких новых."""
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip()
        # Отбрасываем возможный префикс "f(x) =".
        text = text.split("=")[-1].strip().rstrip(".").replace("^", "**")
        try:
            expr = sp.sympify(text, locals={"x": self.x})
        except (sp.SympifyError, SyntaxError, TypeError, ValueError):
            return 0.0
        check_xs = self._xs + [max(self._xs) + 1, max(self._xs) + 2]
        try:
            for xv in check_xs:
                if sp.nsimplify(expr.subs(self.x, xv)) != self._poly.subs(self.x, xv):
                    return 0.0
        except Exception:
            return 0.0
        return 1.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "SymbolicRegressionTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
