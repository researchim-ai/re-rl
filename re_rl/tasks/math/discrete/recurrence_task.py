"""RecurrenceTask — замкнутая форма линейной рекурренты второго порядка.

Рекуррента строится по двум различным целым характеристическим корням, что
гарантирует существование замкнутой формы. Проверка символическая (sympy).
"""

import random
from typing import Any, ClassVar, Dict, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class RecurrenceTask(BaseMathTask):
    """Найти замкнутую форму a(n) линейной рекурренты (проверка через sympy)."""

    TASK_TYPE = "recurrence"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"root_max": 2}, 2: {"root_max": 2}, 3: {"root_max": 3}, 4: {"root_max": 3},
        5: {"root_max": 4}, 6: {"root_max": 4}, 7: {"root_max": 5}, 8: {"root_max": 5},
        9: {"root_max": 6}, 10: {"root_max": 7},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        root_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.root_max = int(root_max if root_max is not None else preset.get("root_max", 4))
        self.augment = augment

        self.n = sp.Symbol("n", integer=True, nonnegative=True)
        self._build()

        recur = f"a(n) = {self.p}·a(n-1) + {self.q}·a(n-2)"
        inits = f"a(0) = {self.a0}, a(1) = {self.a1}"
        description = get_template(
            PROMPT_TEMPLATES["recurrence"], "problem", language,
            augment=augment, recur=recur, inits=inits,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        # Два различных целых корня характеристического уравнения.
        while True:
            r1 = random.randint(-self.root_max, self.root_max)
            r2 = random.randint(-self.root_max, self.root_max)
            if r1 != r2 and r1 != 0 and r2 != 0:
                break
        # x^2 = (r1+r2) x - r1 r2  ->  a(n) = (r1+r2)a(n-1) - r1 r2 a(n-2)
        self.p = r1 + r2
        self.q = -r1 * r2
        self.a0 = random.randint(0, 5)
        self.a1 = random.randint(0, 5)

        n = self.n
        a = sp.Function("a")
        eq = a(n) - self.p * a(n - 1) - self.q * a(n - 2)
        sol = sp.rsolve(eq, a(n), {a(0): self.a0, a(1): self.a1})
        self._ref_expr = sp.simplify(sol)

    @staticmethod
    def _fmt(expr: sp.Expr) -> str:
        return sp.sstr(expr).replace("**", "^")

    def solve(self):
        section = PROMPT_TEMPLATES["recurrence"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._fmt(self._ref_expr)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import sympy_equiv

        if self.final_answer is None:
            self.solve()
        return sympy_equiv(prediction, self._ref_expr, [self.n], local_syms={"n": self.n})

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "RecurrenceTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
