"""GaussianEliminationTask — решение СЛАУ методом Гаусса.

Генерируется невырожденная целочисленная матрица A и целочисленное решение x,
затем b = A·x. Проверка числовая: компоненты решения сравниваются с эталоном.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class GaussianEliminationTask(BaseMathTask):
    """Решить систему линейных уравнений методом Гаусса (числовая проверка)."""

    TASK_TYPE = "gaussian_elimination"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 2, "coef": 4, "sol": 4}, 2: {"size": 2, "coef": 5, "sol": 5},
        3: {"size": 2, "coef": 6, "sol": 6}, 4: {"size": 3, "coef": 4, "sol": 4},
        5: {"size": 3, "coef": 5, "sol": 5}, 6: {"size": 3, "coef": 6, "sol": 6},
        7: {"size": 3, "coef": 7, "sol": 7}, 8: {"size": 4, "coef": 4, "sol": 4},
        9: {"size": 4, "coef": 5, "sol": 5}, 10: {"size": 4, "coef": 6, "sol": 6},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        size: Optional[int] = None,
        coef: Optional[int] = None,
        sol: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.size = int(size if size is not None else preset.get("size", 3))
        self.coef = int(coef if coef is not None else preset.get("coef", 5))
        self.sol_max = int(sol if sol is not None else preset.get("sol", 5))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["gaussian_elimination"], "problem", language,
            augment=augment, system=self._system_str(),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        n = self.size
        while True:
            A = sp.Matrix([[random.randint(-self.coef, self.coef) for _ in range(n)] for _ in range(n)])
            if A.det() != 0:
                break
        self._A = A
        self._x = sp.Matrix([random.randint(-self.sol_max, self.sol_max) for _ in range(n)])
        self._b = A * self._x
        self._solution: List[float] = [float(v) for v in self._x]

    def _system_str(self) -> str:
        n = self.size
        lines = []
        for i in range(n):
            terms = []
            for j in range(n):
                terms.append(f"{self._A[i, j]}·x{j + 1}")
            lines.append(" + ".join(terms) + f" = {self._b[i]}")
        return "\n".join(lines)

    def solve(self):
        section = PROMPT_TEMPLATES["gaussian_elimination"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = ", ".join(f"x{i + 1} = {self._x[i]}" for i in range(self.size))
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction)
        # Убираем метки переменных (x1, x_2, X3, х1 ...), чтобы их индексы не
        # попали в извлечённые числа.
        text = re.sub(r"[xхX]\s*_?\s*\d+", " ", text)
        nums = extract_numbers(text)
        return 1.0 if numbers_match(nums, self._solution) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "GaussianEliminationTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
