"""SymbolicSimplificationTask — упрощение алгебраических выражений.

Задача генерирует выражение в «не упрощённой» форме (произведение множителей
плюс дополнительные слагаемые) и просит привести его к простейшему виду.

Ключевая особенность: проверка ответа выполняется символически через sympy
(``simplify(pred - ref) == 0``), поэтому засчитывается любая математически
эквивалентная форма ответа, а не только совпадающая по строке.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class SymbolicSimplificationTask(BaseMathTask):
    """Упрощение/раскрытие алгебраических выражений (проверка через sympy)."""

    TASK_TYPE = "symbolic_simplification"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_factors": 1, "max_coeff": 3, "num_vars": 1, "extra_terms": 1},
        2: {"num_factors": 2, "max_coeff": 3, "num_vars": 1, "extra_terms": 1},
        3: {"num_factors": 2, "max_coeff": 4, "num_vars": 1, "extra_terms": 1},
        4: {"num_factors": 2, "max_coeff": 5, "num_vars": 1, "extra_terms": 2},
        5: {"num_factors": 2, "max_coeff": 6, "num_vars": 2, "extra_terms": 2},
        6: {"num_factors": 3, "max_coeff": 5, "num_vars": 2, "extra_terms": 2},
        7: {"num_factors": 3, "max_coeff": 6, "num_vars": 2, "extra_terms": 3},
        8: {"num_factors": 3, "max_coeff": 7, "num_vars": 2, "extra_terms": 3},
        9: {"num_factors": 4, "max_coeff": 6, "num_vars": 2, "extra_terms": 3},
        10: {"num_factors": 4, "max_coeff": 8, "num_vars": 2, "extra_terms": 4},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_factors: Optional[int] = None,
        max_coeff: Optional[int] = None,
        num_vars: Optional[int] = None,
        extra_terms: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_factors = int(num_factors if num_factors is not None else preset.get("num_factors", 2))
        self.max_coeff = int(max_coeff if max_coeff is not None else preset.get("max_coeff", 5))
        self.num_vars = int(num_vars if num_vars is not None else preset.get("num_vars", 1))
        self.extra_terms = int(extra_terms if extra_terms is not None else preset.get("extra_terms", 1))
        self.augment = augment

        self._symbols: List[sp.Symbol] = [sp.Symbol("x")]
        if self.num_vars >= 2:
            self._symbols.append(sp.Symbol("y"))

        self._raw_expr = self._generate_expression()
        self._answer_expr = sp.expand(self._raw_expr)
        self._problem_str = self._format_expr(self._raw_expr)

        section = PROMPT_TEMPLATES["symbolic_simplification"]
        description = get_template(
            section,
            "problem",
            language,
            augment=augment,
            expression=self._problem_str,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _generate_expression(self) -> sp.Expr:
        """Строит выражение: произведение линейных множителей + доп. слагаемые."""
        factors = []
        for _ in range(max(1, self.num_factors)):
            var = random.choice(self._symbols)
            a = random.randint(1, self.max_coeff)
            b = random.randint(-self.max_coeff, self.max_coeff)
            factors.append(a * var + b)

        product = sp.Integer(1)
        for f in factors:
            product = product * f  # sympy сохраняет произведение нераскрытым

        extra = sp.Integer(0)
        for _ in range(max(0, self.extra_terms)):
            var = random.choice(self._symbols)
            coeff = random.randint(-self.max_coeff, self.max_coeff)
            degree = random.randint(0, 1)
            extra += coeff * var ** degree

        return product + extra

    @staticmethod
    def _format_expr(expr: sp.Expr) -> str:
        """Строковое представление выражения с ``^`` вместо ``**``."""
        return sp.sstr(expr).replace("**", "^")

    def _parse_expr(self, text: str) -> Optional[sp.Expr]:
        """Пытается распарсить ответ модели в sympy-выражение."""
        local = {str(s): s for s in self._symbols}
        candidates = [text.strip()]
        # На случай, если ответ на отдельной строке или после двоеточия.
        lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
        candidates.extend(reversed(lines))
        for cand in candidates:
            cand = cand.split(":")[-1].strip().rstrip(".").replace("^", "**")
            if not cand:
                continue
            try:
                return sp.sympify(cand, locals=local)
            except (sp.SympifyError, SyntaxError, TypeError, ValueError):
                continue
        return None

    def solve(self):
        section = PROMPT_TEMPLATES["symbolic_simplification"]
        result_str = self._format_expr(self._answer_expr)

        self.solution_steps.append(
            get_template(section, "step_original", self.language, augment=False, expression=self._problem_str)
        )
        self.solution_steps.append(get_template(section, "step_expand", self.language, augment=False))
        self.solution_steps.append(
            get_template(section, "step_simplify", self.language, augment=False, result=result_str)
        )
        self.final_answer = result_str

    def verify(self, prediction: str) -> float:
        """Символическая проверка: любой математически эквивалентный ответ засчитывается."""
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()

        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction
        expr = self._parse_expr(text)
        if expr is None:
            return 0.0
        try:
            return 1.0 if sp.simplify(expr - self._answer_expr) == 0 else 0.0
        except Exception:
            return 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "SymbolicSimplificationTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
