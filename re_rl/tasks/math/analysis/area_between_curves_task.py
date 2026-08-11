"""AreaBetweenCurvesTask — площадь фигуры между двумя кривыми на отрезке.

Верхняя кривая f строится как g + p, где p ≥ 0 на [a, b], поэтому знак разности
известен и площадь вычисляется точно: S = ∫[a,b] (f − g) dx. Числовой ответ.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class AreaBetweenCurvesTask(BaseMathTask):
    """Площадь между кривыми (точный определённый интеграл)."""

    TASK_TYPE = "area_between_curves"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"span": 2, "gdeg": 1, "kmax": 2}, 2: {"span": 2, "gdeg": 1, "kmax": 3},
        3: {"span": 3, "gdeg": 1, "kmax": 3}, 4: {"span": 3, "gdeg": 2, "kmax": 3},
        5: {"span": 4, "gdeg": 2, "kmax": 4}, 6: {"span": 4, "gdeg": 2, "kmax": 4},
        7: {"span": 5, "gdeg": 2, "kmax": 5}, 8: {"span": 5, "gdeg": 2, "kmax": 5},
        9: {"span": 6, "gdeg": 2, "kmax": 6}, 10: {"span": 7, "gdeg": 2, "kmax": 6},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        span: Optional[int] = None,
        gdeg: Optional[int] = None,
        kmax: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.span = int(span if span is not None else preset.get("span", 4))
        self.gdeg = int(gdeg if gdeg is not None else preset.get("gdeg", 2))
        self.kmax = int(kmax if kmax is not None else preset.get("kmax", 4))
        self.augment = augment

        self.x = sp.Symbol("x")
        self._build()

        description = get_template(
            PROMPT_TEMPLATES["area_between_curves"], "problem", language,
            augment=augment, f=self._fmt(self._f), g=self._fmt(self._g),
            a=self.a, b=self.b,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        x = self.x
        self.a = random.randint(-2, 1)
        self.b = self.a + random.randint(1, self.span)
        # Нижняя кривая g — произвольный многочлен.
        g = sum(random.randint(-3, 3) * x ** i for i in range(self.gdeg + 1))
        # Неотрицательная на [a,b] «надбавка» p ≥ 0.
        k = random.randint(1, self.kmax)
        p_choice = random.choice(["arch", "sq", "const"])
        if p_choice == "arch":
            p = k * (x - self.a) * (self.b - x)
        elif p_choice == "sq":
            r = random.randint(self.a, self.b)
            p = k * (x - r) ** 2 + random.randint(0, 2)
        else:
            p = sp.Integer(k)
        self._g = sp.expand(g)
        self._f = sp.expand(g + p)
        self._area = sp.integrate(p, (x, self.a, self.b))

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["area_between_curves"]
        self.solution_steps.append(
            get_template(section, "step_setup", self.language, augment=False, a=self.a, b=self.b)
        )
        result = str(self._area)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], [float(self._area)]) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "AreaBetweenCurvesTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
